from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
import requests

from .forms import FoodItemForm, UserProfileForm, UserRegistrationForm
from .models import ClientMember, FoodItem, UserProfile

# Calorie Ninjas API Key
CALORIE_NINJAS_API_KEY = 'Tjl+m25Qv2Ua6l7K4krOWw==hnR8L33IPJ1lWwwp'


def home_view(request):
  query = request.GET.get('q', '').strip()
  search_results = []

  if query:
    url = f'https://api.calorieninjas.com/v1/nutrition?query={query}'
    headers = {'X-Api-Key': CALORIE_NINJAS_API_KEY}

    try:
      response = requests.get(url, headers=headers)
      if response.status_code == 200:
        data = response.json()
        for item in data.get('items', []):
          search_results.append({
              'item_name': item.get('name').title(),
              'calorie_consumed': round(item.get('calories', 0)),
          })
    except Exception as e:
      print(f'API Fetch Error: {e}')

  context = {
      'query': query,
      'search_results': search_results,
  }
  return render(request, 'home.html', context)


# --- নতুন ভিউ: হোম পেজের ক্যালকুলেটর থেকে প্রোফাইল আপডেট করার জন্য ---
@login_required
def save_calculator_view(request):
  if request.method == 'POST':
    age = request.POST.get('age')
    gender = request.POST.get('gender')
    height = request.POST.get('height')
    weight = request.POST.get('weight')

    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if age:
      user_profile.age = int(age)
    if gender:
      user_profile.gender = gender
    if height:
      user_profile.height_cm = float(height)
    if weight:
      user_profile.weight_kg = float(weight)

    user_profile.save()
    messages.success(
        request, 'Your health metrics updated successfully in Database!'
    )
    return redirect('dashboard')

  return redirect('home')


@login_required
def add_food_from_api(request):
  if request.method == 'POST':
    item_name = request.POST.get('item_name')
    calorie_consumed = request.POST.get('calorie_consumed')

    if item_name and calorie_consumed:
      FoodItem.objects.create(
          user=request.user,
          item_name=item_name,
          calorie_consumed=calorie_consumed,
          date=date.today(),
      )
      messages.success(request, f"'{item_name}' added to today's progress!")
      return redirect('dashboard')

  return redirect('home')


def add_food_from_search(request, food_id):
  if not request.user.is_authenticated:
    messages.error(request, 'Please login first to add food to your log.')
    return redirect('login')

  original_item = FoodItem.objects.get(id=food_id)

  FoodItem.objects.create(
      user=request.user,
      item_name=original_item.item_name,
      calorie_consumed=original_item.calorie_consumed,
      date=date.today(),
  )

  messages.success(
      request, f"'{original_item.item_name}' added to your daily progress!"
  )
  return redirect('dashboard')


def about_view(request):
  return render(request, 'about.html')


def register_view(request):
  if request.method == 'POST':
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')

    if User.objects.filter(username=username).exists():
      return render(
          request, 'register.html', {'error': 'Username already exists!'}
      )

    user = User.objects.create_user(
        username=username, email=email, password=password
    )
    UserProfile.objects.create(user=user)

    login(request, user)
    return redirect('dashboard')

  return render(request, 'register.html')


def login_view(request):
  if request.method == 'POST':
    email = request.POST.get('email')
    password = request.POST.get('password')

    try:
      user_obj = User.objects.get(email=email)
      username = user_obj.username

      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        return redirect('dashboard')
      else:
        return render(
            request, 'login.html', {'error': 'Invalid email or password!'}
        )
    except User.DoesNotExist:
      return render(
          request,
          'login.html',
          {'error': 'User with this email does not exist!'},
      )

  return render(request, 'login.html')


def logout_view(request):
  logout(request)
  return redirect('login')


@login_required
def dashboard_view(request):
  user_profile, created = UserProfile.objects.get_or_create(user=request.user)
  today = date.today()

  if request.method == 'POST':
    # ১. প্রোফাইল আপডেট
    if 'update_profile_btn' in request.POST or 'age' in request.POST:
      age = request.POST.get('age')
      gender = request.POST.get('gender')
      height_cm = request.POST.get('height_cm')
      weight_kg = request.POST.get('weight_kg')

      if age:
        user_profile.age = int(age)
      if gender:
        user_profile.gender = gender
      if height_cm:
        user_profile.height_cm = float(height_cm)
      if weight_kg:
        user_profile.weight_kg = float(weight_kg)

      user_profile.save()
      messages.success(request, 'Profile parameters updated successfully!')
      return redirect('dashboard')

    # ২. খাবার যোগ করার ফর্ম হ্যান্ডলার
    item_name = request.POST.get('item_name')
    calorie_consumed = request.POST.get('calorie_consumed')

    if item_name and calorie_consumed:
      FoodItem.objects.create(
          user=request.user,
          item_name=item_name,
          calorie_consumed=calorie_consumed,
          date=today,
      )
      messages.success(request, f"'{item_name}' added to today's log!")
      return redirect('dashboard')

  today_items = FoodItem.objects.filter(user=request.user, date=today)

  bmr = user_profile.calculate_bmr() if user_profile else 1700
  weight_loss = max(0, bmr - 500)
  weight_gain = bmr + 500

  total_calories = sum(item.calorie_consumed for item in today_items)
  progress_percentage = (
      min(100, round((total_calories / bmr) * 100, 1)) if bmr > 0 else 0
  )

  context = {
      'profile': user_profile,
      'today_items': today_items,
      'bmr': round(bmr, 2),
      'weight_loss': round(weight_loss, 2),
      'weight_gain': round(weight_gain, 2),
      'total_calories': total_calories,
      'progress_percentage': progress_percentage,
  }
  return render(request, 'dashboard.html', context)


def delete_food_view(request, item_id):
  if not request.user.is_authenticated:
    return redirect('login')

  food_item = get_object_or_404(FoodItem, id=item_id, user=request.user)
  item_name = food_item.item_name
  food_item.delete()

  messages.success(request, f"'{item_name}' removed from today's log.")
  return redirect('dashboard')