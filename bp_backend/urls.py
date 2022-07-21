from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from main import views

urlpatterns = [
    #
    # SIGN UP AND LOGIN
    #
    path('signup/', views.SignupView.as_view()),
        # POST only. Creates a new user.  payload must include invite code

    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
        # UNAUTHENTICATED POST; returns you a token

    path('logout/', views.LogoutView.as_view()),
        # AUTHENTICATED GET; kills the active token

    #
    # SKILLS AND ATTRIBUTES
    #
    path('attributes/<slug:category_name>/', views.Attributes.as_view()),
        # UNAUTHENTICATED GET. Returns all atts for a given category
    
    path('skills/', views.SkillsView.as_view()),
        # UNAUTHENTICATED GET returns 20 skills
        # AUTHENTICATED POST to create a new skill; used when someone types a skill we've not heard of
    
    path('skills/<str:pattern>', views.SkillsView.as_view()),
        # UNAUTHENTICATED GET only; returns at most 20 names that match patterns case insensitive.
    
    #
    # Profile and Assessments
    #
    path('profile/', views.MyProfile.as_view()),
        # AUTHENTICATED GET AND PUT.  read/write a JSON blob

    path('assessments/',views.AssessmentsView.as_view()),
        # AUTHENTICATED GET to get them all
        # AUTHENTICATED POST to add a new one

    path('assessment/<int:id>',views.AssessmentView.as_view()),
        # AUTHENTICATED GET, PUT, DELETE. standard CRUD


    #
    # Invites and Anchors
    # 
    path('invites/', views.InvitesView.as_view()),

    #
    # Opportunities
    #
    path('opportunities/',views.OpportunitiesView.as_view()),
        # AUTHENTICATED GET

    path('opportunity/<int:id>/<slug:action>',views.OpportunityView.as_view()),
        # AUTHENTICATED PUT to accept, decline or close

    
    
    # the rest    



    path('endorsements/',views.EndorsementsView.as_view()),
        # GET only
    
    path('endorsement/<slug:action>/<int:id>/',views.EndorsementView.as_view()),
        # authenticated PUT. action can be activate or deactivate

    path('credibility/',views.CredibilityView.as_view()),
        # authenticated GET only

    path('anchors/',views.AnchorsView.as_view()),
        # POST here to pass an anchor (i.e. invite)
        # GET here to see all my active anchors

    path('anchors/<slug:filter>',views.AnchorsView.as_view()),
        # GET here to see all anchors filtered by one of:
        # "sent", "received", "all"

    path('anchor/<int:id>',views.AnchorView.as_view()),
        # GET to see a specific anchor

    path('anchor/<int:id>/<slug:action>',views.AnchorView.as_view()),
        # PUT to "accept", "decline" or "cancel"
    
    path('friends/',views.friendsView.as_view()),
        # authenticated GET

        #
    # Admin and Debugging
    #
    path('admin/', admin.site.urls),

    path('login/', views.LoginView.as_view()),
        # UNAUTHENTICATED PUT only
        # !!! used only for testing



    ]
