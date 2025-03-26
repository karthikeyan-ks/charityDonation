from django.shortcuts import render,redirect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login
from .serializers import UserSerializer, UserRegistrationSerializer
from .models import CustomUser, Organization, ResourceNeed
from donations.models import Donation # Import Donation from donations app
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json
from django.contrib.auth.decorators import user_passes_test
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AdminNotification
from django.db.models import Q
from .forms import ResourceNeedForm
from django.forms import formset_factory

User = get_user_model()

def is_admin(user):
    return user.is_staff

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

@csrf_exempt
def donor_login(request):
    if request.method == 'POST':
        try:
            # Debug: Print request body and content type
            print(f"Request content type: {request.content_type}")
            print(f"Request body: {request.body[:500]}")  # Print first 500 chars to avoid huge logs
            
            # Parse the JSON data
            data = json.loads(request.body)
            print(f"Parsed JSON data: {data}")
            
            email = data.get('email')
            password = data.get('password')
            
            # Check if it's a registration request
            if data.get('register', False):
                print(f"Processing registration for email: {email}")
                # Check if user exists
                if CustomUser.objects.filter(email=email).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'Email already registered'
                    }, status=400)
                
                # Create new user
                user = CustomUser.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    phone_number=data.get('phone_number', ''),
                    address=data.get('address', ''),
                    user_type='DONOR'
                )
                
                print(f"Created new user: {user.email} (ID: {user.id})")
                
                # Create notification for admin
                AdminNotification.objects.create(
                    notification_type='NEW_DONOR',
                    user=user,
                    message=f"New donor {user.get_full_name() or user.email} has registered."
                )
                
                # Log in the user
                user = authenticate(request, username=email, password=password)
                login(request, user)
                
                # Generate JWT token
                refresh = RefreshToken.for_user(user)
                
                response_data = {
                    'success': True,
                    'message': 'Registration successful',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.get_full_name(),
                        'user_type': user.user_type
                    },
                    'token': str(refresh.access_token)
                }
                print(f"Registration successful response: {response_data}")
                return JsonResponse(response_data)
            else:
                # This is a login request
                print(f"Processing login for email: {email}")
            try:
                user = CustomUser.objects.get(email=email, user_type='DONOR')
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    # Generate JWT token
                    refresh = RefreshToken.for_user(user)
                    return JsonResponse({
                        'success': True,
                        'message': 'Login successful',
                        'email': user.email,
                        'user_id': user.id,
                        'name': f"{user.first_name} {user.last_name}",
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid password. Please check your password and try again.'
                    }, status=400)
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'No account found with this email address. Please register first.'
                }, status=400)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            print(f"Request body that failed JSON parsing: {request.body[:500]}")
            return JsonResponse({
                'success': False,
                'message': f'Invalid request format: {str(e)}'
            }, status=400)
        except Exception as e:
            print(f"Unexpected error in donor_login: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'message': f'Server error: {str(e)}'
            }, status=500)
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@csrf_exempt
def organization_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            try:
                user = CustomUser.objects.get(email=email, user_type='ORGANIZATION')
                print(user,password)
                org_profile = Organization.objects.get(user=user)
                
                if org_profile.approval_status != 'APPROVED':
                    return JsonResponse({
                        'success': False,
                        'message': 'Your account is pending approval. Please wait for admin approval.'
                    }, status=400)
                users = User.objects.filter(username=email,password=password)
                user = authenticate(request,username=email, password=password)
                print(user,users)
                if user is not None and user.is_active:
                    login(request, user)
                    # Generate JWT token
                    refresh = RefreshToken.for_user(user)
                    return JsonResponse({
                        'success': True,
                        'message': 'Login successful',
                        'email': user.email,
                        'user_id': user.id,
                        'organization_name': org_profile.name,
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid password or inactive account.'
                    }, status=400)
            except CustomUser.DoesNotExist:
                print("Custom User doesnt exist...")
                return JsonResponse({
                    'success': False,
                    'message': 'No account found with this email address. Please register first.'
                }, status=400)
            except Organization.DoesNotExist:
                print('Organization doesnt exist..')
                return JsonResponse({
                    'success': False,
                    'message': 'Organization profile not found.'
                }, status=400)
        except json.JSONDecodeError:
            print('Parsing error')
            return JsonResponse({
                'success': False,
                'message': 'Invalid request format'
            }, status=400)
        
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)
    

@csrf_exempt
def organization_register(request):
    if request.method == 'POST':
        try:
            # Determine if it's a multipart form or JSON request
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle multipart form data
                email = request.POST.get('email')
                password = request.POST.get('password')
                name = request.POST.get('name')
                phone = request.POST.get('phone')
                license_number = request.POST.get('license_number')
                description = request.POST.get('description')
                first_name = request.POST.get('first_name', '')
                last_name = request.POST.get('last_name', '')
                registration_certificate = request.FILES.get('registration_certificate')
            else:
                # Handle JSON data
                data = json.loads(request.body)
                email = data.get('email')
                password = data.get('password')
                name = data.get('name')
                phone = data.get('phone')
                license_number = data.get('license_number')
                description = data.get('description')
                first_name = data.get('first_name', '')
                last_name = data.get('last_name', '')
                registration_certificate = None
            
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Email already registered'
                }, status=400)
            print(password)
            # Create user with is_active=False until approved
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type='ORGANIZATION',
                is_active=False,  # User will be activated upon approval
                is_organization=True
            )
            user.set_password(password)
            user.save()
            print(user.password)
            
            # Create organization profile
            organization = Organization.objects.create(
                user=user,
                name=name,
                phone=phone,
                license_number=license_number,
                description=description,
                approval_status='PENDING'
            )
            
            # Handle registration certificate upload
            if registration_certificate:
                organization.registration_certificate = registration_certificate
                organization.save()
            
            # Create notification for admin
            AdminNotification.objects.create(
                notification_type='ORGANIZATION_APPROVAL',
                user=user,
                organization=organization,
                message=f"New organization '{name}' is pending approval."
            )
            
            # Send notification to admin
            admin_email = settings.ADMIN_EMAIL if hasattr(settings, 'ADMIN_EMAIL') else 'admin@example.com'
            try:
                send_mail(
                    'New Organization Registration',
                    f'''A new organization "{organization.name}" has registered and is waiting for approval.
                    
                    Organization Details:
                    - Name: {organization.name}
                    - Email: {user.email}
                    - Phone: {organization.phone}
                    - License Number: {organization.license_number}
                    
                            Please review their application in the admin dashboard.
                    ''',
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                    [admin_email],
                    fail_silently=True,
                )
                
                # Send confirmation email to organization
                send_mail(
                    'Registration Received - Pending Approval',
                    f'''Thank you for registering your organization "{organization.name}" with our platform.
                    
                    Your registration is currently pending admin approval. We will review your application
                    and notify you once it has been approved.
                    
                    This process typically takes 1-2 business days.
                    
                    If you have any questions, please contact our support team.
                    ''',
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                    [user.email],
                    fail_silently=True,
                )
            except Exception as e:
                # Log email error but don't fail registration
                print(f"Email sending error: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'message': 'Organization registration successful! Your account is pending approval.',
                'organization_id': organization.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error during registration: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

from django import forms

def organization_form_submit(request):
    ResourceNeedFormSet = formset_factory(ResourceNeedForm, extra=1)

    if request.method == "POST":
        formset = ResourceNeedFormSet(request.POST)
        print("Validation errors:", formset.errors)  # Debugging step

        if formset.is_valid():
            organization = Organization.objects.first()  # Modify this logic as needed

            for form in formset:
                if form.cleaned_data.get("resource"):  # Ensure resource is filled
                    resource_need = form.save(commit=False)
                    resource_need.organization = organization
                    resource_need.save()  # Save before adding ManyToMany relations

                    # Correctly handling ManyToManyField (donation_days)
                    if "donation_days" in form.cleaned_data:
                        resource_need.donation_days.set(form.cleaned_data["donation_days"])

                    resource_need.save()

            return redirect("success_page")  # Redirect after successful submission
    
    else:
        formset = ResourceNeedFormSet()

    return render(request, "orgsubmit.html", {"formset": formset})


def success_page(request):
    return render(request, "success.html")


@login_required
def organization_form_dashboard(request):
    organization = Organization.objects.get(user = request.user)
    resource_need = ResourceNeed.objects.filter(organization=organization)
    return render(request,'organization_dashboard.html',{
        'resource_needs':resource_need
    })

@csrf_exempt
@user_passes_test(is_admin)
def admin_list_pending_organizations(request):
    if request.method == 'GET':
        pending_organizations = Organization.objects.filter(approval_status='PENDING')
        organizations_data = []
        
        for org in pending_organizations:
            organizations_data.append({
                'id': org.id,
                'name': org.name,
                'email': org.user.email,
                'phone': org.phone,
                'license_number': org.license_number,
                'description': org.description,
                'registration_certificate': org.registration_certificate.url if org.registration_certificate else None,
                'created_at': org.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'organizations': organizations_data
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@csrf_exempt
@user_passes_test(is_admin)
def admin_approve_organization(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            org_id = data.get('organization_id')
            action = data.get('action')  # 'approve' or 'reject'
            rejection_reason = data.get('rejection_reason', '')
            
            try:
                organization = Organization.objects.get(id=org_id)
                
                # Mark any pending notification for this organization as read
                pending_notifications = AdminNotification.objects.filter(
                    organization=organization,
                    notification_type='ORGANIZATION_APPROVAL',
                    is_read=False
                )
                pending_notifications.update(is_read=True)
                
                if action == 'approve':
                    organization.approval_status = 'APPROVED'
                    organization.user.is_active = True  # Activate the user account
                    organization.user.save()
                    organization.save()
                    
                    # Create new approval notification
                    AdminNotification.objects.create(
                        notification_type='NEW_ORGANIZATION',
                        user=organization.user,
                        organization=organization,
                        message=f"Organization '{organization.name}' has been approved and activated."
                    )
                    
                    # Send approval email to organization
                    send_mail(
                        'Organization Registration Approved',
                        f'''Congratulations! Your organization "{organization.name}" has been approved.
                        You can now log in to your account and start creating campaigns.
                        ''',
                        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                        [organization.user.email],
                        fail_silently=True,
                    )
                elif action == 'reject':
                    organization.approval_status = 'REJECTED'
                    organization.rejection_reason = rejection_reason
                    organization.save()
                    
                    # Keep the user account inactive
                    organization.user.is_active = False
                    organization.user.save()
                    
                    # Create rejection notification
                    AdminNotification.objects.create(
                        notification_type='NEW_ORGANIZATION',
                        user=organization.user,
                        organization=organization,
                        message=f"Organization '{organization.name}' has been rejected. Reason: {rejection_reason}"
                    )
                    
                    # Send rejection email to organization
                    send_mail(
                        'Organization Registration Rejected',
                        f'''We are sorry to inform you that your organization "{organization.name}" registration has been rejected.
                        
                        Reason: {rejection_reason}
                        
                            If you believe this is a mistake or if you would like to provide additional information,
                        please contact our support team.
                        ''',
                        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                        [organization.user.email],
                        fail_silently=True,
                    )
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid action. Use "approve" or "reject".'
                    }, status=400)
                    
            except Organization.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Organization not found'
                }, status=404)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
            
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_list_organizations(request):
    """
    Get a list of all organizations for admin panel
    """
    # Only allow admin users
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized. Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get query parameters for filtering
        status_filter = request.query_params.get('status', 'all')
        search = request.query_params.get('search', None)
        
        # Start with all organizations
        organizations = Organization.objects.all()
        
        # Apply filters if provided
        if status_filter and status_filter.upper() in ['APPROVED', 'PENDING', 'REJECTED'] and status_filter != 'all':
            organizations = organizations.filter(approval_status=status_filter.upper())
        
        if search:
            organizations = organizations.filter(
                Q(name__icontains=search) | 
                Q(user__email__icontains=search) |
                Q(license_number__icontains=search)
            )
            
        # Order by most recent first
        organizations = organizations.order_by('-created_at')
        
        # Calculate statistics
        total = Organization.objects.count()
        pending = Organization.objects.filter(approval_status='PENDING').count()
        active = Organization.objects.filter(approval_status='APPROVED').count()
        
        # Prepare response data
        org_data = []
        for org in organizations:
            org_data.append({
                'id': org.id,
                'name': org.name,
                'email': org.user.email,
                'phone': org.phone,
                'license_number': org.license_number,
                'status': org.approval_status,
                'created_at': org.created_at.isoformat(),
                'location': org.user.address or 'N/A'
            })
        
        return Response({
            'success': True,
            'organizations': org_data,
            'stats': {
                'total': total,
                'pending': pending,
                'active': active
            }
        })
        
    except Exception as e:
        print(f"Error in admin_list_organizations: {str(e)}")
        return Response(
            {
                'success': False,
                'message': f'An error occurred while retrieving organizations: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_organization(request, org_id):
    # Only allow admin users
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Only admin users can access this endpoint'
        }, status=403)
    
    try:
        organization = Organization.objects.get(id=org_id)
        
        org_data = {
            'id': organization.id,
            'name': organization.name,
            'email': organization.user.email,
            'phone': organization.phone,
            'license_number': organization.license_number,
            'description': organization.description,
            'status': organization.approval_status,
            'registration_date': organization.created_at.isoformat(),
            'type': organization.user.get_user_type_display(),
            'location': organization.user.address or 'N/A',
            'certificate_url': organization.registration_certificate.url if organization.registration_certificate else None
        }
        
        return JsonResponse(org_data)
        
    except Organization.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Organization not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@csrf_exempt
def admin_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_staff:
                login(request, user)
                # Generate JWT token
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful',
                    'username': user.username,
                    'user_id': user.id,
                    'email': user.email,
                    'token': str(refresh.access_token)
                })
            elif user is not None:
                return JsonResponse({
                    'success': False,
                    'message': 'Access denied. You must be an admin to log in.'
                }, status=403)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid username or password. Please try again.'
                }, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request format'
            }, status=400)
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    print(f"Admin dashboard access attempt by user: {request.user.username}, is_staff: {request.user.is_staff}")
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized. Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get statistics
        total_donors = CustomUser.objects.filter(user_type='DONOR').count()
        total_organizations = Organization.objects.count()
        pending_organizations = Organization.objects.filter(approval_status='PENDING').count()
        
        # Get recent notifications
        recent_notifications = AdminNotification.objects.all().order_by('-created_at')[:5]
        notifications_data = []
        for notification in recent_notifications:
            data = {
                'id': notification.id,
                'type': notification.notification_type,
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
            }
            notifications_data.append(data)
        
        # Get pending organization approvals
        pending_orgs = Organization.objects.filter(approval_status='PENDING').order_by('-created_at')[:5]
        org_data = []
        for org in pending_orgs:
            org_data.append({
                'id': org.id,
                'name': org.name,
                'date': org.created_at.isoformat(),
                'status': org.approval_status
            })
        
        # Return dashboard data
        return Response({
            'stats': {
                'total_donors': total_donors,
                'total_organizations': total_organizations,
                'pending_organizations': pending_organizations
            },
            'notifications': notifications_data,
            'organization_approvals': org_data,
            'recent_donations': []  # Simplified to avoid potential errors
        })
    except Exception as e:
        print(f"Error in admin_dashboard: {str(e)}")
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_notifications(request):
    """
    Get a list of admin notifications
    """
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get query parameters
    is_read = request.query_params.get('is_read', None)
    notification_type = request.query_params.get('type', None)
    limit = int(request.query_params.get('limit', 20))
    
    # Build query
    query = AdminNotification.objects.all()
    if is_read is not None:
        query = query.filter(is_read=is_read.lower() == 'true')
    if notification_type:
        query = query.filter(notification_type=notification_type)
    
    # Get notifications
    notifications = query.order_by('-created_at')[:limit]
    
    # Serialize data
    notifications_data = []
    for notification in notifications:
        data = {
            'id': notification.id,
            'type': notification.notification_type,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at,
            'user': {
                'id': notification.user.id,
                'email': notification.user.email,
                'name': notification.user.get_full_name() or notification.user.username
            }
        }
        
        if notification.organization:
            data['organization'] = {
                'id': notification.organization.id,
                'name': notification.organization.name,
                'status': notification.organization.approval_status
            }
        
        notifications_data.append(data)
    
    return Response({
        'notifications': notifications_data,
        'unread_count': AdminNotification.objects.filter(is_read=False).count()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id=None):
    """
    Mark a notification as read, or mark all as read if notification_id is None
    """
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if notification_id:
        # Mark specific notification as read
        try:
            notification = AdminNotification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return Response({'success': True, 'message': 'Notification marked as read'})
        except AdminNotification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Mark all as read
        AdminNotification.objects.filter(is_read=False).update(is_read=True)
        return Response({'success': True, 'message': 'All notifications marked as read'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_organization(request, org_id, action):
    # Only allow admin users
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized. Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        organization = Organization.objects.get(id=org_id)
        
        # Mark any pending notification for this organization as read
        pending_notifications = AdminNotification.objects.filter(
            organization=organization,
            notification_type='ORGANIZATION_APPROVAL',
            is_read=False
        )
        pending_notifications.update(is_read=True)
        
        if action == 'approve':
            organization.approval_status = 'APPROVED'
            organization.user.is_active = True  # Activate the user account
            organization.user.save()
            organization.save()
            
            # Create new approval notification
            AdminNotification.objects.create(
                notification_type='NEW_ORGANIZATION',
                user=organization.user,
                organization=organization,
                message=f"Organization '{organization.name}' has been approved and activated."
            )
            
            # Send approval email to organization
            try:
                send_mail(
                    'Organization Registration Approved',
                    f'''Congratulations! Your organization "{organization.name}" has been approved.
                    You can now log in to your account and start creating campaigns.
                    ''',
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                    [organization.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email sending error: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'message': 'Organization approved successfully'
            })
            
        elif action == 'reject':
            organization.approval_status = 'REJECTED'
            organization.rejection_reason = request.data.get('rejection_reason', '')
            organization.save()
            
            # Keep the user account inactive
            organization.user.is_active = False
            organization.user.save()
            
            # Create rejection notification
            AdminNotification.objects.create(
                notification_type='NEW_ORGANIZATION',
                user=organization.user,
                organization=organization,
                message=f"Organization '{organization.name}' has been rejected."
            )
            
            # Send rejection email to organization
            try:
                send_mail(
                    'Organization Registration Rejected',
                    f'''We are sorry to inform you that your organization "{organization.name}" registration has been rejected.
                    
                    If you believe this is a mistake or if you would like to provide additional information,
                    please contact our support team.
                    ''',
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                    [organization.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email sending error: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'message': 'Organization rejected successfully'
            })
            
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action. Use "approve" or "reject".'
            }, status=400)
            
    except Organization.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Organization not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)

@api_view(['GET'])
def check_organization_status(request, org_id):
    """
    Check the approval status of an organization
    """
    try:
        organization = Organization.objects.get(id=org_id)
        
        # Return basic status information
        response_data = {
            'id': organization.id,
            'status': organization.approval_status,
            'email': organization.user.email
        }
        
        # If approved, include authentication tokens
        if organization.approval_status == 'APPROVED':
            # Generate JWT token
            refresh = RefreshToken.for_user(organization.user)
            
            response_data.update({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': organization.user.id,
                'organization_name': organization.name
            })
        
        return Response(response_data)
        
    except Organization.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Organization not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_list_donors(request):
    """
    Get a list of all donors for admin panel
    """
    # Only allow admin users
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized. Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get query parameters for filtering
        search = request.query_params.get('search', None)
        
        # Start with all donor users
        donors = CustomUser.objects.filter(user_type='DONOR')
        
        # Apply search filter if provided
        if search:
            donors = donors.filter(
                Q(username__icontains=search) | 
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
            
        # Order by most recent first
        donors = donors.order_by('-registration_date')
        
        # Calculate statistics
        total_donors = CustomUser.objects.filter(user_type='DONOR').count()
        active_donors = CustomUser.objects.filter(user_type='DONOR', is_active=True).count()
        
        # Prepare response data
        donor_data = []
        for donor in donors:
            donor_data.append({
                'id': donor.id,
                'username': donor.username,
                'first_name': donor.first_name,
                'last_name': donor.last_name,
                'name': f"{donor.first_name} {donor.last_name}".strip() or donor.username,
                'email': donor.email,
                'phone': donor.phone_number,
                'address': donor.address,
                'is_active': donor.is_active,
                'profile_picture': donor.profile_picture.url if donor.profile_picture else None,
                'registration_date': donor.registration_date.isoformat() if donor.registration_date else None
            })
            
        return Response({
            'success': True,
            'donors': donor_data,
            'stats': {
                'total': total_donors,
                'active': active_donors
            }
        })
        
    except Exception as e:
        print(f"Error in admin_list_donors: {str(e)}")
        return Response(
            {
                'success': False,
                'message': f'An error occurred while retrieving donors: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_donor(request, donor_id):
    """
    Get detailed information about a donor for admin panel
    """
    # Only allow admin users
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized. Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        donor = CustomUser.objects.get(id=donor_id, user_type='DONOR')
        
        # You can add donation history or other related data here
        
        donor_data = {
            'id': donor.id,
            'username': donor.username,
            'first_name': donor.first_name,
            'last_name': donor.last_name,
            'name': f"{donor.first_name} {donor.last_name}".strip() or donor.username,
            'email': donor.email,
            'phone': donor.phone_number,
            'address': donor.address,
            'is_active': donor.is_active,
            'profile_picture': donor.profile_picture.url if donor.profile_picture else None,
            'registration_date': donor.registration_date.isoformat() if donor.registration_date else None
        }
        
        return Response({
            'success': True,
            'donor': donor_data
        })
        
    except CustomUser.DoesNotExist:
        return Response(
            {
                'success': False,
                'message': 'Donor not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error in admin_get_donor: {str(e)}")
        return Response(
            {
                'success': False,
                'message': f'An error occurred while retrieving donor details: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
