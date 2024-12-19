from flask import render_template, request, redirect, url_for, session, flash, Blueprint

admin = Blueprint('admin', __name__)

@admin.route('/')
def home():
    return