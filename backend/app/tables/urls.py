from django.urls import path

from . import views

app_name = "tables"

urlpatterns = [
    path("", views.new_table, name="new"),
    path("<uuid:table_id>/", views.table_detail, name="detail"),
    path("<uuid:table_id>/actions/", views.submit_action, name="submit_action"),
    path("<uuid:table_id>/next-hand/", views.next_hand, name="next_hand"),
]