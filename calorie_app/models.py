from django.db import models
from django.contrib.auth.models import User

# ১. ইউজার প্রোফাইল মডেল
class UserProfile(models.Model):
    GENDER_CHOICES = (('Male', 'Male'), ('Female', 'Female'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(default=25)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    height_cm = models.FloatField(default=170)
    weight_kg = models.FloatField(default=70)

    def calculate_bmr(self):
        if self.gender == 'Male':
            return 66.47 + (13.75 * self.weight_kg) + (5.003 * self.height_cm) - (6.755 * self.age)
        else:
            return 655.1 + (9.563 * self.weight_kg) + (1.850 * self.height_cm) - (4.676 * self.age)

# ২. একাধিক মানুষের রেকর্ড রাখার জন্য নতুন Client Member মডেল
class ClientMember(models.Model):
    GENDER_CHOICES = (('Male', 'Male'), ('Female', 'Female'))
    
    trainer = models.ForeignKey(User, on_delete=models.CASCADE) # কে এন্ট্রি দিচ্ছে
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    height_cm = models.FloatField()
    weight_kg = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    # BMR calculation
    def calculate_bmr(self):
        if self.gender == 'Male':
            return 66.47 + (13.75 * self.weight_kg) + (5.003 * self.height_cm) - (6.755 * self.age)
        else:
            return 655.1 + (9.563 * self.weight_kg) + (1.850 * self.height_cm) - (4.676 * self.age)

    # BMI calculation
    def calculate_bmi(self):
        height_m = self.height_cm / 100
        if height_m > 0:
            return self.weight_kg / (height_m ** 2)
        return 0

    # BMI status
    def bmi_status(self):
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi <= 24.9:
            return "Normal"
        elif 25 <= bmi <= 29.9:
            return "Overweight"
        else:
            return "Obese"

class FoodItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    calorie_consumed = models.FloatField()
    date = models.DateField(auto_now_add=True)