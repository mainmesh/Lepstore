from django.shortcuts import redirect
from django.urls import reverse

from cart.cart import Cart


class AgeVerificationMiddleware:
    """Middleware to enforce age verification for cannabis purchases.

    - Redirects to the age verification page when a user attempts checkout
      with cannabis items and has not verified their age in session.
    - This is a lightweight safeguard — further KYC and license checks
      must be implemented for production.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Only protect the checkout and order creation endpoints
        checkout_paths = [reverse('orders:checkout')]

        if path in checkout_paths:
            try:
                cart = Cart(request)
                if cart.contains_cannabis():
                    # If user is authenticated, check their profile first
                    if request.user.is_authenticated:
                        try:
                            if getattr(request.user, 'userprofile', None) and request.user.userprofile.age_verified:
                                pass
                            else:
                                return redirect(f"{reverse('accounts:age_verification')}?next={path}")
                        except Exception:
                            return redirect(f"{reverse('accounts:age_verification')}?next={path}")
                    else:
                        # Guest users: rely on session flag
                        if not request.session.get('is_age_verified'):
                            return redirect(f"{reverse('accounts:age_verification')}?next={path}")
            except Exception:
                # Fail open on unexpected errors but do not break the request
                pass

        response = self.get_response(request)
        return response
