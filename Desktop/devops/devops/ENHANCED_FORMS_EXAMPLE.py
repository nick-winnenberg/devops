"""
Enhanced Forms for Multiple Owner Support

These forms would support the enhanced model with many-to-many ownership relationships.
"""

from django import forms
from django.contrib.auth.models import User


# These would replace the existing forms if you implement multiple ownership
class EnhancedOfficeForm(forms.ModelForm):
    """
    Enhanced office form supporting multiple owners.
    """
    
    class Meta:
        model = Office  # Would use the enhanced Office model
        fields = ['name', 'number', 'address', 'city', 'state', 'zip_code', 'primary_owner', 'owners']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Limit owner choices to current user's owners
            user_owners = Owner.objects.filter(user=user)
            self.fields['primary_owner'].queryset = user_owners
            self.fields['owners'].queryset = user_owners
            
        # Customize widgets
        self.fields['owners'].widget = forms.CheckboxSelectMultiple()
        self.fields['owners'].help_text = "Select all owners for this office. Primary owner will be the main contact."


class EnhancedReportForm(forms.ModelForm):
    """
    Enhanced report form with multiple owner selection capability.
    """
    
    class Meta:
        model = Report  # Would use the enhanced Report model  
        fields = ['subject', 'transcript', 'content', 'vibe', 'calltype', 
                 'office', 'primary_owner', 'additional_owners']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        office = kwargs.pop('office', None)
        primary_owner = kwargs.pop('primary_owner', None)
        
        super().__init__(*args, **kwargs)
        
        # Make fields optional where appropriate
        self.fields['office'].required = False
        self.fields['additional_owners'].required = False
        
        if user:
            user_owners = Owner.objects.filter(user=user)
            self.fields['primary_owner'].queryset = user_owners
            self.fields['additional_owners'].queryset = user_owners
            
        # If office context provided, limit owners to that office's owners
        if office:
            office_owners = office.owners.all()
            self.fields['primary_owner'].queryset = office_owners
            self.fields['additional_owners'].queryset = office_owners
            self.fields['office'].initial = office
            
        # If primary owner provided, set as initial
        if primary_owner:
            self.fields['primary_owner'].initial = primary_owner
            
        # Customize widgets
        self.fields['additional_owners'].widget = forms.CheckboxSelectMultiple()
        self.fields['additional_owners'].help_text = "Select any additional owners involved in this communication."


class OwnerSelectionWidget(forms.Widget):
    """
    Custom widget for complex owner selection scenarios.
    """
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        
    def render(self, name, value, attrs=None, renderer=None):
        # Custom HTML for owner selection with visual grouping
        html = f'''
        <div class="owner-selection-widget">
            <div class="primary-owner">
                <label for="id_{name}_primary">Primary Owner (Main Contact):</label>
                <select id="id_{name}_primary" name="{name}_primary" class="form-control">
                    <!-- Options populated by form -->
                </select>
            </div>
            <div class="additional-owners mt-3">
                <label>Additional Owners Involved:</label>
                <div class="checkbox-group">
                    <!-- Checkboxes populated by form -->
                </div>
            </div>
            <div class="office-context mt-3">
                <label for="id_{name}_office">Related Office (Optional):</label>
                <select id="id_{name}_office" name="{name}_office" class="form-control">
                    <option value="">-- Select Office --</option>
                    <!-- Options populated by form -->  
                </select>
            </div>
        </div>
        '''
        return html