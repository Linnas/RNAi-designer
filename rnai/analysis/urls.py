from django.urls import path
from . import views

urlpatterns = [
    path('createDatabase', views.create_database),
    path('getAllDatabasesInfo', views.get_all_databases_info),
    path('run_pipeline', views.run_pipeline),
    path('process_data', views.process_data),
]