import requests
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import UserRegistrationForm, UserProfileForm, FoodItemForm
from .models import UserProfile, FoodItem, ClientMember

# Calorie Ninjas API Key
CALORIE_NINJAS_API_KEY = 'Tjl+m25Qv2Ua6l7K4krOWw==hnR8L33IPJ1lWwwp'


def home_view(request):
    query = request.GET.get('q', '').strip()
    search_results = []

    if query:
        # Calorie Ninjas API Call
        url = f'https://api.calorieninjas.com/v1/nutrition?query={query}'
        headers = {'X-Api-Key': CALORIE_NINJAS_API_KEY}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    search_results.append({
                        'item_name': item.get('name').title(),
                        'calorie_consumed': round(item.get('calories', 0))
                    })
        except Exception as e:
            print(f"API Fetch Error: {e}")

    context = {
        'query': query,
        'search_results': search_results,
    }
    return render(request, 'home.html', context)


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
                date=date.today()
            )
            messages.success(request, f"'{item_name}' added to today's progress!")
            return redirect('dashboard')

    return redirect('home')


def add_food_from_search(request, food_id):
    if not request.user.is_authenticated:
        messages.error(request, "Please login first to add food to your log.")
        return redirect('login')
        
    original_item = FoodItem.objects.get(id=food_id)
    
    FoodItem.objects.create(
        user=request.user,
        item_name=original_item.item_name,
        calorie_consumed=original_item.calorie_consumed,
        date=date.today()
    )
    
    messages.success(request, f"'{original_item.item_name}' added to your daily progress!")
    return redirect('dashboard')


def about_view(request):
    return render(request, 'about.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists!'})

        user = User.objects.create_user(username=username, email=email, password=password)
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
                return render(request, 'login.html', {'error': 'Invalid email or password!'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'User with this email does not exist!'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = UserProfile.objects.filter(user=request.user).first()
    today = date.today()

    if request.method == "POST":
        item_name = request.POST.get('item_name')
        calorie_consumed = request.POST.get('calorie_consumed')

        if item_name and calorie_consumed:
            FoodItem.objects.create(
                user=request.user,
                item_name=item_name,
                calorie_consumed=calorie_consumed,
                date=today
            )
            messages.success(request, f"'{item_name}' added to today's log!")
            return redirect('dashboard')

    today_items = FoodItem.objects.filter(user=request.user, date=today)

    bmr = user_profile.calculate_bmr() if user_profile else 1700
    weight_loss = max(0, bmr - 500)
    weight_gain = bmr + 500

    total_calories = sum(item.calorie_consumed for item in today_items)
    progress_percentage = min(100, round((total_calories / bmr) * 100, 1)) if bmr > 0 else 0

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