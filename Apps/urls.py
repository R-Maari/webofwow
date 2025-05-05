from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/',views.register,name='register'),
    path('otp/', views.otp_verify, name='otp_verify'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('sucess/',views.sucess,name='sucess'), 
    path('dashboard/',views.dashboard,name='dashboard'),
    path('login/',views.login,name='login'),
    path('weather/', views.weather, name='weather'),
    path('ocr/', views.ocr, name='ocr'),
    path('md5/', views.md5, name='md5'),
    path('nearby/', views.nearby, name='nearby'),
    path('download_video/', views.download_video, name='download_video'),
    path('download_success/', views.download_success, name='download_success'),
    path('timing/', views.timing, name='timing'),
    path('timer/', views.timer, name='timer'),
    path('stopwatch/', views.stopwatch, name='stopwatch'),
    path('international-time/', views.international_time, name='international_time'),
    path('pdfmaker/',views.upload_file,name="upload_file"),
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('music/', views.music, name='music'),
    path('convert/', views.convert, name='convert'),
    path('tick_tac/', views.tick_tac, name='tick_tac'), 
    path('puzzle/', views.puzzle_game_view, name='puzzle_game'),
    path('brain/', views.brain_game_view, name='brain_game'),
    path('guess/', views.guess_number, name='guess_number'),
    path('sudoku/', views.sudoku_view, name='sudoku'),
    path("dictionary/", views.home, name="dictionary"),
    path('qrgenerator/', views.generate_qr, name='generate_qr'),
    path('generate-password/',views.generate_password, name='generate_password'),
    path('color_picker/', views.color_picker, name='color_picker'),  
    path('<str:short_code>', views.redirect_url, name='redirect_url'),

  ]


