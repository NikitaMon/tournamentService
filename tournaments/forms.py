from datetime import date, datetime
from django import forms
from tournaments.models import Registration, Tournament, FightingStyle, TournamentCategory, TournamentCategoryTemplate
from django.core.exceptions import ValidationError
from django.utils import timezone

# class TournamentForm(forms.ModelForm):
#     # поле для видов борьбы с чекбоксами
#     fighting_styles = forms.ModelMultipleChoiceField(
#         queryset=FightingStyle.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False,
#         label="Виды борьбы"
#     )
    
#     class Meta:
#         model = Tournament
#         fields = '__all__'
#         widgets = {
#             'early_registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'regular_registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'late_registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'description': forms.Textarea(attrs={'rows': 3}),
#         }

#     def __init__(self, *args, **kwargs):
#         self.user = kwargs.pop('user', None)    
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             if field_name != 'fighting_styles':
#                 field.widget.attrs['class'] = 'form-control'
#         if self.instance.pk:
#             self.fields['fighting_styles'].initial = self.instance.fighting_styles.all()

#     def save(self, commit=True):
#         tournament = super().save(commit=False)
#         if commit:
#             tournament.save()
#             self.save_m2m()
#             tournament.fighting_styles.set(self.cleaned_data['fighting_styles'])
#         return tournament
    
    
#     def clean(self):
#         cleaned_data = super().clean()
#         dates = [
#             ('early_registration_end', 'Ранняя регистрация'),
#             ('regular_registration_end', 'Обычная регистрация'),
#             ('late_registration_end', 'Поздняя регистрация'),
#             ('registration_deadline', 'Окончание регистрации')
#         ]
        
#         if dates[0][0] == None and dates[2][0] == None:
#             for i in range(len(dates)-1):
#                 if cleaned_data.get(dates[i][0]) >= cleaned_data.get(dates[i+1][0]):
#                     raise ValidationError(
#                         f"{dates[i][1]} должна заканчиваться раньше {dates[i+1][1]}"
#                     )
        
#         # Проверка что выбраны виды борьбы
#         if not cleaned_data.get('fighting_styles'):
#             raise ValidationError("Выберите хотя бы один вид борьбы")
        
#         return cleaned_data
    
#     def clean_image(self):
#         image = self.cleaned_data.get('image')
#         if image:
#             # Проверка размера файла (не более 2MB)
#             if image.size > 2 * 1024 * 1024:
#                 raise forms.ValidationError("Изображение должно быть меньше 2MB")
            
#             # Проверка расширения файла
#             valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
#             if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
#                 raise forms.ValidationError("Поддерживаются только JPG, PNG или WebP")
#         return image
    

class TournamentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['tournament_category', 'weight_category', 'belt_level']
        widgets = {
            'weight_category': forms.Select(attrs={'disabled': True}),
            'belt_level': forms.Select()
        }

    def __init__(self, *args, tournament=None, **kwargs):
        self.user = kwargs.pop('user', None)
        self.tournament = tournament
        super().__init__(*args, **kwargs)
        if tournament:
            self.fields['tournament_category'].queryset = tournament.tournament_categories.all()
            self.fields['weight_category'].choices = []  # Будет заполнено через AJAX
            self.fields['belt_level'].choices = []  # Будет заполнено через AJAX

    def clean(self):
        def calculate_age(birth_date):
            today = date.today()
            return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        cleaned_data = super().clean()
        category = cleaned_data.get('tournament_category')
        weight = cleaned_data.get('weight_category')
        belt = cleaned_data.get('belt_level')
        
        if category and weight and belt:
            # Проверка на повторную регистрацию
            if self.tournament:
                existing_reg = Registration.objects.filter(
                    tournament=self.tournament,
                    tournament_category=category
                )
                
                if self.user and self.user.is_authenticated:
                    existing_reg = existing_reg.filter(profile_user=self.user.profile_user)
                elif 'email' in self.data:
                    existing_reg = existing_reg.filter(unregistered_participant__email=self.data['email'])
                
                if existing_reg.exists():
                    raise ValidationError(
                        "Вы уже зарегистрированы в этой категории. "
                        "Выберите другую категорию или отмените предыдущую регистрацию."
                    )

            # Проверка веса
            if weight not in category.weight_categories:
                raise ValidationError({
                    'weight_category': f"Выбранный вес ({weight} кг) не доступен в этой категории. "
                                     f"Доступные веса: {', '.join(map(str, category.weight_categories))} кг"
                })
            
            # Проверка пояса
            if belt not in category.belt_levels:
                raise ValidationError({
                    'belt_level': f"Выбранный пояс ({belt}) не доступен в этой категории. "
                                f"Доступные пояса: {', '.join(category.belt_levels)}"
                })
            
            # Проверка возраста
            age = None
            if self.user and self.user.is_authenticated:
                # Для авторизованных пользователей берем возраст из профиля
                profile = self.user.profile_user
                age = calculate_age(profile.birth_date)
            elif 'birth_date' in self.data:
                # Для неавторизованных пользователей берем возраст из формы
                try:
                    birth_date = datetime.strptime(self.data['birth_date'], '%Y-%m-%d').date()
                    age = calculate_age(birth_date)
                except (ValueError, TypeError):
                    raise ValidationError({
                        'birth_date': "Некорректная дата рождения"
                    })
            
            if age is not None:
                template = category.template
                if template.age_from and age < template.age_from:
                    raise ValidationError({
                        'tournament_category': f"Вы слишком молоды для этой категории. "
                                            f"Ваш возраст: {age} лет. "
                                            f"Минимальный возраст: {template.age_from} лет"
                    })
                if template.age_to and age > template.age_to:
                    raise ValidationError({
                        'tournament_category': f"Вы слишком взрослы для этой категории. "
                                            f"Ваш возраст: {age} лет. "
                                            f"Максимальный возраст: {template.age_to} лет"
                    })
        
        return cleaned_data


# class TournamentCategoryForm(forms.ModelForm):
#     class Meta:
#         model = TournamentCategory
#         fields = ['weight_categories', 'edit']
        
#     def __init__(self, *args, **kwargs):
#         template = kwargs.pop('template', None)
#         super().__init__(*args, **kwargs)
#         if template:
#             self.fields['weight_categories'].initial = template.weight_categories


class TournamentForm(forms.ModelForm):
    fighting_styles = forms.ModelMultipleChoiceField(
        queryset=FightingStyle.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Виды борьбы"
    )
    
    # Добавляем поле для выбора категорий
    categories = forms.ModelMultipleChoiceField(
        queryset=TournamentCategoryTemplate.objects.none(),  # Будет заполнено динамически
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Выберите категории"
    )
    
    class Meta:
        model = Tournament
        fields = [
            'title', 'image', 'location', 'description',
            'fighting_styles', 'early_registration_start', 'early_registration_price',
            'regular_registration_start', 'regular_registration_price',
            'late_registration_start', 'late_registration_price',
            'registration_deadline', 'tournament_start', 'tournament_end',
            'newbies', 'status'
        ]
        widgets = {
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'tournament_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'tournament_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'early_registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'regular_registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'late_registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'newbies': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'newbies': 'Разрешить участие новичков',
            'status': 'Статус турнира'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс form-control только для текстовых полей
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs['class'] = 'form-control'
        
        # Исключаем опцию "отменено" из выбора статуса
        self.fields['status'].choices = [
            choice for choice in self.fields['status'].choices 
            if choice[0] != 'cancelled'
        ]
        
        # Если форма была отправлена, заполняем queryset для категорий
        if 'fighting_styles' in self.data:
            try:
                style_ids = [int(x) for x in self.data.getlist('fighting_styles')]
                self.fields['categories'].queryset = TournamentCategoryTemplate.objects.filter(
                    fighting_style__id__in=style_ids
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # Если редактируем существующий турнир
            self.fields['categories'].queryset = TournamentCategoryTemplate.objects.filter(
                fighting_style__in=self.instance.fighting_styles.all()
            )

class WeightCategoriesForm(forms.Form):
    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if categories:
            for category in categories:
                self.fields[f'weights_{category.id}'] = forms.CharField(
                    label=f"{category.name} (веса, кг) [{category.fighting_style.name}]",
                    initial=", ".join(str(w) for w in category.weight_categories),
                    help_text="Введите веса через запятую",
                    required=False
                )
                
                # Добавляем поле для выбора поясов
                self.fields[f'belts_{category.id}'] = forms.MultipleChoiceField(
                    label=f"{category.name} (пояса) [{category.fighting_style.name}]",
                    choices=[
                        ('белый', 'Белый'),
                        ('синий', 'Синий'),
                        ('фиолетовый', 'Фиолетовый'),
                        ('коричневый', 'Коричневый'),
                        ('черный', 'Черный'),
                    ],
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                    help_text="Выберите допустимые пояса для категории"
                )