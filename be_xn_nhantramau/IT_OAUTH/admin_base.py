from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages


class ConfirmActionAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('confirm_action/', self.admin_site.admin_view(self.confirm_action), name='confirm_action'),
        ]
        return custom_urls + urls

    def response_action(self, request, queryset):
        """
        Override response_action to handle password confirmation for all actions.
        """
        action = request.POST.get('action')
        selected = request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME)

        if action and selected:
            # Save the action and selected items in session
            request.session['action_to_confirm'] = action
            request.session['selected_items'] = selected
            return HttpResponseRedirect('confirm_action/')

        return super().response_action(request, queryset)

    def confirm_action(self, request):
        """
        Handle the password confirmation and perform the action if the password is correct.
        """
        if request.method == 'POST':
            # Get the password from the form
            password = request.POST.get('password')
            # Authenticate the user
            user = authenticate(request, username=request.user.username, password=password)
            if user is not None:
                # If authentication is successful, proceed with the action
                login(request, user)
                action = request.session.pop('action_to_confirm', None)
                selected = request.session.pop('selected_items', [])

                if action:
                    # Dynamically retrieve the action method
                    action_method = getattr(self, action, None)
                    if action_method:
                        queryset = self.model.objects.filter(pk__in=selected)
                        response = action_method(request, queryset)

                        # If the action method returns a response, return it
                        if response:
                            return response
                        else:
                            messages.success(request, "Action performed successfully.")
                            return HttpResponseRedirect('../')
                    else:
                        messages.error(request, f"The action '{action}' could not be found.")
                        return HttpResponseRedirect('../')

            else:
                # If authentication fails, show an error message
                messages.error(request, "Password is incorrect.")

        # If the method is GET or authentication fails, render the confirmation template
        return render(request, 'admin/confirm_action.html')
