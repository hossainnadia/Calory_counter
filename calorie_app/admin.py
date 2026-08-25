from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, ClientMember, FoodItem

# 1. Customizing Built-in User Admin to remove First Name and Last Name
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)


# 2. UserProfile Admin Setup
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # list_display এ get_bmr এবং get_bmi যোগ করা হয়েছে
    list_display = ('user', 'age', 'gender', 'height_cm', 'weight_kg', 'get_bmr', 'get_bmi')

    # BMR বের করার কাস্টম মেথড
    def get_bmr(self, obj):
        return round(obj.calculate_bmr(), 2)
    get_bmr.short_description = 'BMR (kcal)'

    # BMI বের করার কাস্টম মেথড
    def get_bmi(self, obj):
        height_m = obj.height_cm / 100
        if height_m > 0:
            bmi = obj.weight_kg / (height_m ** 2)
            return round(bmi, 2)
        return 0
    get_bmi.short_description = 'BMI Score'


# 3. ClientMember Admin Setup
@admin.register(ClientMember)
class ClientMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer', 'gender', 'age', 'height_cm', 'weight_kg', 'get_bmr', 'get_bmi', 'bmi_status')

    def get_bmr(self, obj):
        return round(obj.calculate_bmr(), 2)
    get_bmr.short_description = 'BMR (kcal)'

    def get_bmi(self, obj):
        return round(obj.calculate_bmi(), 2)
    get_bmi.short_description = 'BMI Score'


# 4. FoodItem Admin Setup
@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'user', 'calorie_consumed', 'date')
    list_filter = ('date', 'user')  # অতিরিক্ত সুবিধা: তারিখ ও ইউজার দিয়ে ফিল্টার করা যাবে
    search_fields = ('item_name', 'user__username')