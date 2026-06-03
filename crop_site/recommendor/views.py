from django.shortcuts import render,redirect
from recommendor.models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
# Create your views here.
def home(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_predictions = prediction.objects.count()
    return render(request, "home.html",locals())

def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not name or not phone or not email or not password:
            messages.error(request, "Please fill all required fields")
            return redirect("signup")
        if len(password) < 6:
            messages.error(request,"Password should contain minimum 6 characters")
            return redirect("signup")
        if User.objects.filter(username=email).exists():
            messages.error(request, "Account already exists with this email")
            return redirect("signup")
        user = User.objects.create_user(username=email,password=password)
        if " " in name:
            first , last = name.split(" ",1)
        else:
            first , last = name, ""
        user.first_name , user.last_name = first , last
        user.save()
        UserProfile.objects.create(user=user,phone=phone)
        login(request,user)
        messages.success(request,"Account Created Successfully,Welcome!")
        return redirect("predict")
    return render(request, "signup.html")
from .ml.loader import predict_one, load_bundle
from django.contrib.auth.decorators import login_required,user_passes_test

@login_required

def predict_view(request):
    feature_order = load_bundle()["feature_cols"]
    result = None
    last_data = None

    if request.method == "POST":
        data = {}
        try:
            for c in feature_order:
                data[c] = float(request.POST.get(c))
        except (TypeError, ValueError):
            messages.error(request, "Please enter valid numeric values.")
            return redirect("Predict")

        label = predict_one(data)

        # Save to DB with explicit fields
        prediction.objects.create(
    user=request.user,
    n=data.get("N"),
    p=data.get("P"),
    k=data.get("K"),
    temperature=data.get("temperature"),
    humidity=data.get("humidity"),
    ph=data.get("ph"),
    rainfall=data.get("rainfall"),
    predicted_label=label
)

        result = label
        last_data = data
        messages.success(request, f"Recommended Crop: {label.title()}")

    return render(request, "predict.html", locals())
def logout_view(request):
    logout(request)
    messages.success(request,"Logout Successfully.")
    return redirect("login")
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request,username=username,password=password)
        if not user:
            messages.error(request, "Invalid Login Credentials")
            return redirect("login")
        login(request,user)
        messages.success(request,"Logged In Successfully!")
        return redirect("predict")
    return render(request,"login.html")

@login_required
def user_history_view(request):
    Predictions = prediction.objects.filter(user=request.user)
    return render(request, "history.html", {"prediction": Predictions})

from django.shortcuts import get_object_or_404
@login_required
def user_delete_prediction(request,id):
    Prediction = get_object_or_404(prediction,id=id,user=request.user)
    Prediction.delete()
    messages.success(request,"Entry removed from history")
    return redirect("user_history")

@login_required
def profile_view(request):
    # Get the single profile object for the logged-in user
    profile = UserProfile.objects.filter(user=request.user).first()

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")

        # Update user name
        if name:
            parts = name.split(" ", 1)
            request.user.first_name = parts[0]
            request.user.last_name = parts[1] if len(parts) > 1 else ""

        # Update profile phone if profile exists
        if profile:
            profile.phone = phone
            profile.save()

        # Save user changes
        request.user.save()

        messages.success(request, "Profile updated")

    full_name = request.user.get_full_name()
    return render(request, "profile.html", locals())

@login_required
def change_view(request):
    # Get the single profile object for the logged-in user

    if request.method == "POST":
        current = request.POST.get("current_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        # Update user name
        if not request.user.check_password(current):
            messages.error(request,"Current Password is incorrect.")
            return redirect("change")
        if len(new) < 6:
            messages.error(request,"New Password must be atleast 6 characters.")
            return redirect("change")
        if new != confirm:
            messages.error(request,"New Password do not match.")
            return redirect("change")
        # Update profile phone if profile exists
        request.user.set_password(new)
        request.user.save()
        user = authenticate(request,username=request.user.username,password = new)
        if user:
            login(request,user)
            messages.success(request, "Password changed successfully")
            return redirect("change")
    return render(request, "change.html", locals())
def admin_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request,username=username,password=password)
        if not user:
            messages.error(request, "Invalid Login Credentials")
            return redirect("admin")
        if not user.is_staff:
            messages.error(request, "You are not authorized for admin panel.")
            return redirect("admin")
        login(request,user)
        messages.success(request,"Logged In Successfully!")
        return redirect("dashboard")
    return render(request,"admin.html")
def is_staff(user):
    return user.is_authenticated and user.is_staff

from django.db.models import Count
from django.utils import timezone
import json
from datetime import timedelta
@user_passes_test(is_staff,login_url='admin')
def dashboard_view(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_predictions = prediction.objects.count()
    crop_qs = (
        prediction.objects.values('predicted_label')
        .annotate(c = Count('id'))
        .order_by('-c')[:10]
    )
    crop_labels = [i['predicted_label'].title() for i in crop_qs]
    crop_counts = [i['c'] for i in crop_qs]

    today = timezone.localdate()
    days = [today-timedelta(days=i) for i in range(6,-1,-1)]

    day_labels = [d.strftime("%d %b") for d in days]
    day_counts = [prediction.objects.filter(created_at__date = d).count() for d in days]

    context ={
        "total_users" : total_users,
        "total_predictions" : total_predictions,
        "crop_labels_json" : json.dumps(crop_labels),
        "crop_counts_json" : json.dumps(crop_counts),
        "day_labels_json" : json.dumps(day_labels),
        "day_counts_json" : json.dumps(day_counts),
    }

    return render(request, "dashboard.html", context)

@user_passes_test(is_staff,login_url='admin')
def displayuser_view(request):
    users = User.objects.filter(is_staff=False)
    
    return render(request, "displayuser.html", {"users":users})

@user_passes_test(is_staff,login_url='admin')
def admin_user_delete(request,id):
    user = get_object_or_404(User,id=id)
    user.delete()
    messages.success(request,"user deleted")
    return redirect("displayuser")

from django.utils.dateparse import parse_date
@user_passes_test(is_staff,login_url='admin')
def adminprediction_view(request):
    qs = prediction.objects.select_related("user").all()
    crop = request.GET.get('crop')
    start = request.GET.get('start')
    end = request.GET.get('end')
    if crop:
        qs=qs.filter(predicted_label__iexact = crop)

    d_start = parse_date(start) if start else None
    d_end = parse_date(end) if end else None

    if d_start:
        qs=qs.filter(created_at__date__gte = d_start)

    if d_end:
        qs=qs.filter(created_at__date__lte = d_end)

    crops = (prediction.objects
             .order_by('predicted_label')
             .values_list('predicted_label',flat=True)
             .distinct())

    context ={
        "qs" : qs,
        "crops" : crops,
        "current_crop" : crop,
        "start" : start,
        "end" : end
        
    }
    return render(request, "predictions.html", context)

@user_passes_test(is_staff,login_url='admin')
def admin_prediction_delete(request, id):
    predictions = get_object_or_404(prediction, id=id)
    predictions.delete()
    messages.success(request, "Prediction deleted")
    return redirect("adminprediction")

def admin_logout_view(request):
    logout(request)
    messages.success(request,"Logout Successfully.")
    return redirect("admin")