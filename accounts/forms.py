from datetime import date
from django import forms
from accounts.models import UnregisteredParticipant, Profile_user, Profile_organizer
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
import re
import logging

from accounts.models.coach import Coach

logger = logging.getLogger(__name__)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'})
    )
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]+$',
                message='Имя пользователя может содержать только буквы, цифры и символ подчеркивания'
            )
        ],
        min_length=3,
        max_length=30
    )
    user_type = forms.ChoiceField(
        choices=[
            ('participant', 'Участник'),
            ('organizer', 'Организатор'),
            ('coach', 'Тренер')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='participant',
        label='Тип пользователя'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка виджетов для полей пароля
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
        
        # Добавление help_text для полей
        self.fields['username'].help_text = 'От 3 до 30 символов. Только буквы, цифры и _'
        self.fields['password1'].help_text = '''
            <ul class="password-requirements">
                <li>Минимум 8 символов</li>
                <li>Хотя бы одна буква</li>
                <li>Хотя бы одна цифра</li>
            </ul>
        '''
        self.fields['password2'].help_text = 'Введите тот же пароль для подтверждения'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует")
        if len(username) < 3:
            raise forms.ValidationError("Имя пользователя должно содержать минимум 3 символа")
        if len(username) > 30:
            raise forms.ValidationError("Имя пользователя не должно превышать 30 символов")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Введите корректный email адрес")
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        errors = []
        
        if len(password1) < 8:
            errors.append("Пароль должен содержать минимум 8 символов")
        if not re.search(r'[A-Za-z]', password1):
            errors.append("Пароль должен содержать хотя бы одну букву")
        if not re.search(r'\d', password1):
            errors.append("Пароль должен содержать хотя бы одну цифру")
            
        if errors:
            raise forms.ValidationError(errors)
            
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data.get('user_type')
        logger.info(f"Saving user with type: {user_type}")
        
        if commit:
            user.save()
            logger.info(f"User saved with ID: {user.id}")
            
            # Создаем или получаем группу в зависимости от типа пользователя
            if user_type == 'organizer':
                group, created = Group.objects.get_or_create(name='organizer')
            elif user_type == 'coach':
                group, created = Group.objects.get_or_create(name='coach')
            else:
                group, created = Group.objects.get_or_create(name='participant')
            
            # Добавляем пользователя в группу
            user.groups.add(group)
            logger.info(f"User added to group: {group.name}")
            
            # Создаем соответствующий профиль
            try:
                if user_type == 'organizer':
                    profile = Profile_organizer.objects.create(user=user)
                elif user_type == 'coach':
                    profile = Coach.objects.create(user=user)
                else:
                    profile = Profile_user.objects.create(user=user)
                logger.info(f"Profile created: {profile}")
            except Exception as e:
                logger.error(f"Error creating profile: {str(e)}")
                raise
        
        return user


class CoachProfileForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = ['first_name', 'last_name', 'surname', 'phone', 'birth_date', 'gender']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[('', 'Выберите пол'), ('М', 'М'), ('Ж', 'Ж')]),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'surname': 'Отчество',
            'phone': 'Телефон',
            'birth_date': 'Дата рождения',
            'gender': 'Пол',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.birth_date:
            self.initial['birth_date'] = self.instance.birth_date.strftime('%Y-%m-%d')


# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']
#         widgets = {
#             'first_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True})
#         }


# class ProfileUserForm(forms.ModelForm):
#     """
#     Для пользователя
#     """
#     phone = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
#         validators=[RegexValidator(regex=r'^(\+7|8)[\d\- ]{10,15}$', message="Номер должен состоять из чисел")]
#     )
#     class Meta:
#         model = Profile_user
#         fields = ['avatar', 'surname', 'phone', 'birth_date', 'gender']
#         widgets = {
#             'surname': forms.TextInput(attrs={'class': 'form-control'}),
 
#             'birth_date': forms.DateInput(attrs={
#                 'class': 'form-control',
#                 'type': 'date'
#             }),
#             'gender': forms.Select(attrs={'class': 'form-select'}),
#             'avatar': forms.FileInput(attrs={
#                 'class': 'form-control',
#                 'accept': 'image/*',
#                 'style': 'display: none;' 
#             })
#         }
        
#     def clean_phone(self):
#         phone = self.cleaned_data.get('phone')
            
#         # Удаляем все нецифровые символы
#         cleaned_phone = re.sub(r'[^\d]', '', phone)
        
#         # Проверяем длину 
#         if len(cleaned_phone) != 11:
#             raise ValidationError("Номер должен содержать 10 цифр")
            
#         return cleaned_phone

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance.birth_date:
#             self.initial['birth_date'] = self.instance.birth_date.strftime('%Y-%m-%d')
#         self.fields['avatar'].widget.attrs.update({'accept': 'image/*'})



# class ProfileOrganizerForm(forms.ModelForm):
#     """
#     Для организатора
#     """
#     company_phone = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': '+7 (XXX) XXX-XX-XX'
#         }),
#         validators=[
#             RegexValidator(
#                 regex=r'^(\+7|8)[\d\- ]{10,15}$',
#                 message="Номер должен состоять из чисел"
#             )
#         ]
#     )
#     class Meta:
#         model = Profile_organizer
#         fields = ['surname', 'avatar', 'tax_id', 'company_phone', 'company_name', 'company_address']
#         widgets = {
#             'surname': forms.TextInput(attrs={'class': 'form-control'}),
#             'company_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'company_address': forms.TextInput(attrs={'class': 'form-control'}),
#             'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
#             'avatar': forms.FileInput(attrs={
#                 'class': 'form-control',
#                 'accept': 'image/*',
#                 'style': 'display: none;' 
#             })
#         }
        
#     def clean_phone(self):
#         company_phone = self.cleaned_data.get('company_phone')
            
#         # Удаляем все нецифровые символы
#         cleaned_phone = re.sub(r'[^\d]', '', company_phone)
        
#         # Проверяем длину 
#         if len(cleaned_phone) != 11:
#             raise ValidationError("Номер должен содержать 10 цифр")
            
#         return cleaned_phone

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['avatar'].widget.attrs.update({'accept': 'image/*'})


class UnregisteredParticipantForm(forms.ModelForm):
    class Meta:
        model = UnregisteredParticipant
        fields = ['first_name', 'last_name', 'surname', 'gender', 'birth_date', 'phone', 'email']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'})
        }


class OrganizerProfileForm(forms.ModelForm):
    class Meta:
        model = Profile_organizer
        fields = ['first_name', 'last_name', 'surname', 'company_name', 
                 'company_address', 'company_phone', 'tax_id']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'company_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
    