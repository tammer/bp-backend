"""bp_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('attributes/<slug:category_name>/', views.Attributes.as_view()),
    path('profile/', views.MyProfile.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    # path('accounts/',views.AccountView.as_view()), Why is this here?

    path('anchors/',views.AnchorsView.as_view()),
        # POST here to pass an anchor (i.e. invite)
        # GET here to see all my active anchors

    path('anchors/<slug:filter>',views.AnchorsView.as_view()),
        # GET here to see all anchors filtered by one of:
        # "sent", "received", "all"

    path('anchor/<int:id>',views.AnchorView.as_view()),
        # GET to see a specific anchor

    path('anchor/<int:id>/<slug:action>',views.AnchorView.as_view()),
        # PUT to "accept", "reject" or "cancel"

    ]
