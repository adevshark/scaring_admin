from django.conf.urls.static import static
from django.urls import path

from Scaring import settings
from scaringadmin import views

urlpatterns = [
    path('signin', views.sign_in, name='sign_in'),
    path('signup', views.sign_up, name='sign_up'),
    path('signout', views.sign_out, name='sign_out'),
    path('forgetpassword', views.forgetpassword, name='forgetpassword'),
    path('password-reset/<str:token>', views.admin_password_reset, name='admin_password_reset'),
    path('password-save/', views.admin_password_reset_post, name='admin_password_reset_post'),
    path('phonenumberverify', views.phonenumberverify, name='phonenumberverify'),

    path('sendEmailApi', views.sendEmailApi, name='sendEmailApi'),
    path('imageDownloadApi', views.imageDownloadApi, name='imageDownloadApi'),

    path('success', views.success_page, name='success'),
    path('accountKit', views.accountKit, name='accountKit'),

    # -------------------- ADMIN DASHBOARD -----------------------
    path('', views.index, name='admin_index'),
    path('users', views.userList, name='users'),
    path('sites', views.sites, name='sites'),
    path('data', views.data, name='data'),
    path('addUser', views.addUser, name='addUser'),
    path('editUser', views.editUser, name='editUser'),
    path('getUser', views.getUser, name='getUser'),
    path('deleteUser', views.deleteUser, name='deleteUser'),
    path('getMinedData', views.getMinedData, name='getMinedData'),
    path('blockUser', views.blockUser, name='blockUser'),
    path('unBlockUser', views.unBlockUser, name='unBlockUser'),
    path('scarpingSettings', views.scarpingSettings, name='scarpingSettings'),
    path('apiSettings', views.apiSettings, name='apiSettings'),
    path('emailSettings', views.emailSettings, name='emailSettings'),
    path('smsSettings', views.smsSettings, name='smsSettings'),
    path('proxySettings', views.proxySettings, name='proxySettings'),
    path('addSite', views.addSite, name='addSite'),
    path('getSite', views.getSite, name='getSite'),
    path('editSite', views.editSite, name='editSite'),
    path('deleteSite', views.deleteSite, name='deleteSite'),
    path('updateCronJobStatus', views.updateCronJobStatus, name='updateCronJobStatus'),
    path('update_email_setting', views.update_email_setting, name='update_email_setting'),
    path('updateTwilio', views.updateTwilio, name='updateTwilio'),
    path('updateFacebookAccountKit', views.updateFacebookAccountKit, name='updateFacebookAccountKit'),
    path('getEveyMonthData', views.getEveyMonthData, name='updateTwilio'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('edit_user_profile', views.edit_user_profile, name='edit_user_profile'),
    path('addProxy', views.addProxy, name='addProxy'),
    path('deleteProxy', views.deleteProxy, name='deleteProxy'),
    path('setProxy', views.setProxy, name='setProxy'),
    path('removeData', views.removeData, name='removeData'),
    path('getMinedDataByID', views.getMinedDataByID, name='getMinedDataByID'),
    path('updateMinedData', views.updateMinedData, name='updateMinedData'),
    path('update_admin_email', views.update_admin_email, name='update_admin_email'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
