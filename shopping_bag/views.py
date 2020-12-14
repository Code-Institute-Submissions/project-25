from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages

from products.models import Product


# Create your views here.
def view_shopping_bag(request):
    """ A view to return the shopping bag contents page page """

    return render(request, 'shopping_bag/shopping-bag.html')


def add_to_shopping_bag(request, item_id):
    print("add_to_shopping_bag")
    # Get the product from the Product model \
    # using the item_id as the primary key
    product = get_object_or_404(Product, pk=item_id)
    # Obtain the quantity value from the form
    quantity = int(request.POST.get('quantity'))
    # Obtain the size value from the form
    size = request.POST['product_size']
    print(size)
    # And the redirect_url from the form hidden-field
    redirect_url = request.POST.get('redirect_url')

    # For storing the shopping_bag contents to the session
    """
    1. Request the shopping_bag from the session variables
       or return an empty dictionary.
    """
    shopping_bag = request.session.get('shopping_bag', {})
    """
    2. Check if the item_id of the product to be added
       is already in the shopping_bag.
       If it is then just update the quantity.
       Else add the item_id and the quantity to
       the shopping_bag
    """
    if item_id in list(shopping_bag.keys()):
        if size in shopping_bag[item_id]['items_by_size'].keys():
            shopping_bag[item_id]['items_by_size'][size] += quantity
            messages.success(request,
                             f'Updates size {size.upper()} {product.name}\
                             quantity to \
                             {shopping_bag[item_id]["items_by_size"][size]}.')
        else:
            shopping_bag[item_id]['items_by_size'][size] = quantity
            messages.success(request,
                             f'Added size {size.upper()}\
                             {product.name} to your bag.')
    else:
        shopping_bag[item_id] = {'items_by_size': {size: quantity}}
        messages.success(request,
                         f'Added size {size.upper()}\
                         {product.name} to your bag.')

    """
    3. Now store the shopping_bag to the session
    variables as session.shopping_bag
    """
    request.session['shopping_bag'] = shopping_bag
    """
    4. Now redirect the user back to the url they were on previously
    """
    print("bag")
    print(request.session['shopping_bag'])
    return redirect(redirect_url)


def edit_shopping_bag(request, item_id):
    print("edit_shopping_bag")
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    size = request.POST['product_size']
    redirect_url = request.POST.get('redirect_url')
    shopping_bag = request.session.get('shopping_bag', {})

    shopping_bag[item_id]['items_by_size'][size] = quantity
    messages.success(request,
                     f'Updated size {size.upper()} {product.name}\
                       quantity to \
                       {shopping_bag[item_id]["items_by_size"][size]}.')

    request.session['shopping_bag'] = shopping_bag
    return redirect(reverse('view_shopping_bag'))
