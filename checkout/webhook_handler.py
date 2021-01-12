from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
import json
import time


class StripeWH_Handler:
    """
    Handle Stripe webhooks
    """
    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        # Send the order confirmation email
        # 1. Get the customers email from the order
        cust_email = order.email
        print(cust_email)
        # 2. Compile the email subject txt file and order as strings
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        # 3. Compile the email body txt file and order as strings
        # and the contact_email variable from settings
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled Webhook received: {event["type"]}',
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle a payment succeeded webhook event
        """
        # To submit the payment form using when the success webhook
        # is returned using the data and metadata sent with the paymentIntent
        intent = event.data.object
        # Get the order details from the paymentIntent data
        pid = intent.id
        shopping_bag = intent.metadata.shopping_bag
        save_info = intent.metadata.save_info
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Iterate thru' the shipping details address dictionary to replace
        # empty strings with None values so the data is filled with clean
        # values
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info checkbos is checked.
        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

        # Process
        # Preset a flag to false and an attempt flag to 1
        order_exists = False
        attempt = 1
        # Now check if the order already exists in the database
        # using the data from the payment intent
        # Try this 5 times in case the form submitted from the browser is slow
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=shopping_bag,
                    stripe_pid=pid,
                )
                # If the order is found in the database,
                # then set the order_exists flag to True
                order_exists = True
                break

            # If the order does not exist then we need to recreate the order
            # form using the form data from the paymentIntent
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        # After attempt 5 check the order_exists flag
        if order_exists:
            # If order_exists=true,
            # Send the order confirmation email
            # and return a 200 Http response to Stripe
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Payment succeeded Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200
            )
        else:
            # If order_exists=False, try to recreate the order
            order = None
            try:
                # Create the order
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=shopping_bag,
                    stripe_pid=pid,
                )
            # Iterate through the items in the order using the json version
            # of the shopping bag in the paymentIntent as though to submit
            # the OrderLineItem's
                for item_id, item_data in json.loads(shopping_bag).items():
                        product = Product.objects.get(id=item_id)
                        if isinstance(item_data, int):
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=item_data,
                            )
                            order_line_item.save()
                        else:
                            for size, quantity in item_data['items_by_size'].items():
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_size=size,
                                )
                                order_line_item.save()
            # If there is a problem with the recreating the Order
            # then delete this recreated Order and return this error to
            # Stripe and Stripe will try again later
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Payment succeeded Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Payment succeeded Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle a payment failed webhook event
        """
        return HttpResponse(
            content=f'Payment failed Webhook received: {event["type"]}',
            status=200
        )
