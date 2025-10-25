from django import forms
from django.core.exceptions import ValidationError
from .models import FloodRecord
from datetime import datetime
from django.utils import timezone

# Updated BARANGAYS list with real Silay City barangays
BARANGAYS = [
    ('Balaring', 'Balaring'),
    ('Barangay I (Pob.)', 'Barangay I (Pob.)'),
    ('Barangay II (Pob.)', 'Barangay II (Pob.)'),
    ('Barangay III (Pob.)', 'Barangay III (Pob.)'),
    ('Barangay IV (Pob.)', 'Barangay IV (Pob.)'),
    ('Barangay V (Pob.)', 'Barangay V (Pob.)'),
    ('Barangay VI Pob. (Hawaiian)', 'Barangay VI Pob. (Hawaiian)'),
    ('Eustaquio Lopez', 'Eustaquio Lopez'),
    ('Guimbala-on', 'Guimbala-on'),
    ('Guinhalaran', 'Guinhalaran'),
    ('Kapitan Ramon', 'Kapitan Ramon'),
    ('Lantad', 'Lantad'),
    ('Mambulac', 'Mambulac'),
    ('Rizal', 'Rizal'),
    ('Bagtic', 'Bagtic'),
    ('Patag', 'Patag'),
]

EVENT_TYPES = [
    ('Flood', 'Flood'),
    ('Flash Flood', 'Flash Flood'),
]

class FloodRecordForm(forms.ModelForm):
    affected_barangays = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'id_affected_barangays', 
            'readonly': 'readonly',
            'placeholder': 'No barangays selected yet'
        }),
        required=True,
        help_text='Select barangays from the dropdown below.',
        error_messages={
            'required': 'Please select at least one affected barangay.'
        }
    )
    
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'max': datetime.now().strftime('%Y-%m-%dT%H:%M')
        }),
        help_text='Select the date and time of the flood event.',
        error_messages={
            'required': 'Please provide the date and time of the flood event.',
            'invalid': 'Please enter a valid date and time.'
        }
    )
    
    event = forms.ChoiceField(
        choices=EVENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Choose the type of flood event.',
        error_messages={
            'required': 'Please select an event type.'
        }
    )

    class Meta:
        model = FloodRecord
        fields = ['event', 'date', 'affected_barangays', 'casualties_dead', 'casualties_injured', 'casualties_missing',
                  'affected_persons', 'affected_families', 'houses_damaged_partially', 'houses_damaged_totally',
                  'damage_infrastructure_php', 'damage_agriculture_php', 'damage_institutions_php',
                  'damage_private_commercial_php', 'damage_total_php']
        
        widgets = {
            'casualties_dead': forms.NumberInput(attrs={'min': '0', 'value': '0', 'placeholder': '0'}),
            'casualties_injured': forms.NumberInput(attrs={'min': '0', 'value': '0', 'placeholder': '0'}),
            'casualties_missing': forms.NumberInput(attrs={'min': '0', 'value': '0', 'placeholder': '0'}),
            'affected_persons': forms.NumberInput(attrs={'min': '0', 'value': '0', 'placeholder': '0'}),
            'affected_families': forms.NumberInput(attrs={'min': '0', 'value': '0', 'placeholder': '0'}),
            'houses_damaged_partially': forms.NumberInput(attrs={'min': '0', 'value': '0', 'placeholder': '0'}),
            'houses_damaged_totally': forms.NumberInput(attrs={'min': '0', 'value': '0', 'placeholder': '0'}),
            'damage_infrastructure_php': forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'value': '0', 'placeholder': '0.00'}),
            'damage_agriculture_php': forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'value': '0', 'placeholder': '0.00'}),
            'damage_institutions_php': forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'value': '0', 'placeholder': '0.00'}),
            'damage_private_commercial_php': forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'value': '0', 'placeholder': '0.00'}),
            'damage_total_php': forms.NumberInput(attrs={'min': '0', 'step': '0.01', 'value': '0', 'placeholder': '0.00'}),
        }

    def clean_affected_barangays(self):
        """Validate affected barangays field."""
        affected_barangays = self.cleaned_data.get('affected_barangays', '').strip()
        
        if not affected_barangays:
            raise ValidationError("At least one barangay must be selected.")
        
        # Split and validate each barangay
        barangay_list = [b.strip() for b in affected_barangays.split(',') if b.strip()]
        
        if not barangay_list:
            raise ValidationError("At least one barangay must be selected.")
        
        # Get valid barangay names
        valid_barangays = [b[0] for b in BARANGAYS]
        
        # Check if all selected barangays are valid
        invalid_barangays = [b for b in barangay_list if b not in valid_barangays]
        if invalid_barangays:
            raise ValidationError(f"Invalid barangay names: {', '.join(invalid_barangays)}")
        
        # Remove duplicates and rejoin
        unique_barangays = list(dict.fromkeys(barangay_list))
        return ', '.join(unique_barangays)

    def clean_date(self):
        """Validate that the date is not in the future."""
        date = self.cleaned_data.get('date')
        
        if date and date > timezone.now():
            raise ValidationError("The flood event date cannot be in the future.")
        
        return date

    def clean_casualties_dead(self):
        """Validate casualties_dead is non-negative."""
        value = self.cleaned_data.get('casualties_dead', 0)
        if value < 0:
            raise ValidationError("Number of deaths cannot be negative.")
        return value

    def clean_casualties_injured(self):
        """Validate casualties_injured is non-negative."""
        value = self.cleaned_data.get('casualties_injured', 0)
        if value < 0:
            raise ValidationError("Number of injured cannot be negative.")
        return value

    def clean_casualties_missing(self):
        """Validate casualties_missing is non-negative."""
        value = self.cleaned_data.get('casualties_missing', 0)
        if value < 0:
            raise ValidationError("Number of missing persons cannot be negative.")
        return value

    def clean_affected_persons(self):
        """Validate affected_persons is non-negative."""
        value = self.cleaned_data.get('affected_persons', 0)
        if value < 0:
            raise ValidationError("Number of affected persons cannot be negative.")
        return value

    def clean_affected_families(self):
        """Validate affected_families is non-negative."""
        value = self.cleaned_data.get('affected_families', 0)
        if value < 0:
            raise ValidationError("Number of affected families cannot be negative.")
        return value

    def clean(self):
        """Perform cross-field validation."""
        cleaned_data = super().clean()
        
        # Validate that affected persons >= affected families (assuming average family size >= 1)
        affected_persons = cleaned_data.get('affected_persons', 0)
        affected_families = cleaned_data.get('affected_families', 0)
        
        if affected_families > 0 and affected_persons < affected_families:
            self.add_error('affected_persons', 
                "Number of affected persons should be at least equal to the number of affected families.")
        
        # Validate damage amounts
        damage_fields = [
            'damage_infrastructure_php',
            'damage_agriculture_php',
            'damage_institutions_php',
            'damage_private_commercial_php'
        ]
        
        for field in damage_fields:
            value = cleaned_data.get(field, 0)
            if value < 0:
                self.add_error(field, "Damage amount cannot be negative.")
        
        # Calculate and validate total damage
        total_calculated = sum([
            cleaned_data.get('damage_infrastructure_php', 0),
            cleaned_data.get('damage_agriculture_php', 0),
            cleaned_data.get('damage_institutions_php', 0),
            cleaned_data.get('damage_private_commercial_php', 0)
        ])
        
        total_entered = cleaned_data.get('damage_total_php', 0)
        
        # Allow for small floating point differences
        if abs(total_calculated - total_entered) > 0.01:
            # Auto-correct the total
            cleaned_data['damage_total_php'] = total_calculated
            # Optionally, you can add a warning
            # self.add_error('damage_total_php', 
            #     f"Total damage auto-corrected to match sum of individual damages: ₱{total_calculated:,.2f}")
        
        # Validate houses damaged
        houses_partial = cleaned_data.get('houses_damaged_partially', 0)
        houses_total = cleaned_data.get('houses_damaged_totally', 0)
        
        if houses_partial < 0:
            self.add_error('houses_damaged_partially', "Number cannot be negative.")
        if houses_total < 0:
            self.add_error('houses_damaged_totally', "Number cannot be negative.")
        
        return cleaned_data