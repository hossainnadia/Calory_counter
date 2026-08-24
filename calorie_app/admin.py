from django.contrib import admin
from .models import UserProfile, ClientMember, FoodItem

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # list_display এ get_bmr এবং get_bmi যোগ করা হয়েছে
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


@admin.register(ClientMember)
class ClientMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer', 'gender', 'age', 'height_cm', 'weight_kg', 'get_bmr', 'get_bmi', 'bmi_status')

    def get_bmr(self, obj):
        return round(obj.calculate_bmr(), 2)
    get_bmr.short_description = 'BMR (kcal)'

    def get_bmi(self, obj):
        return round(obj.calculate_bmi(), 2)
    get_bmi.short_description = 'BMI Score'


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'user', 'calorie_consumed', 'date')