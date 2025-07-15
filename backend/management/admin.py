from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import Group
from .models import *
from django.utils.formats import localize

admin.site.unregister(Group)

class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_formatted', 'transaction_count')
    list_filter = ('type',)
    search_fields = ('nom',)
    list_per_page = 20
    
    def type_formatted(self, obj):
        color = 'green' if obj.type == 'ENTREE' else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_type_display()
        )
    type_formatted.short_description = 'Type'

    def transaction_count(self, obj):
        count = obj.transactions.count()  # Remplacez 'transaction_set' par 'transactions'
        url = reverse('admin:management_transaction_changelist') + f'?categorie__id__exact={obj.id}'
        return format_html('<a href="{}">{} transactions</a>', url, count)
    transaction_count.short_description = 'Transactions'

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'utilisateur_link', 'montant_colored', 'categorie_link', 'type', 'description_short')
    list_filter = ('type', 'date', 'categorie')
    search_fields = ('description', 'utilisateur__username', 'categorie__nom')
    list_select_related = ('utilisateur', 'categorie')
    date_hierarchy = 'date'
    list_per_page = 30
    
    fieldsets = (
        (None, {
            'fields': ('utilisateur', 'type', 'montant', 'date')
        }),
        ('Détails', {
            'fields': ('categorie', 'description'),
            'classes': ('collapse',)
        }),
    )
    
   
    
    def montant_colored(self, obj):
        color = 'green' if obj.type == 'ENTREE' else 'red'
        return format_html(
            '<span style="color: {};">{} €</span>',
            color,
            localize(obj.montant)  # Formatage localisé
    )
    montant_colored.short_description = 'Montant'
    montant_colored.admin_order_field = 'montant'

    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
    
    def utilisateur_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.utilisateur.id])
        return format_html('<a href="{}">{}</a>', url, obj.utilisateur.username)
    utilisateur_link.short_description = 'Utilisateur'
    
    def categorie_link(self, obj):
        url = reverse('admin:management_categorie_change', args=[obj.categorie.id])
        return format_html('<a href="{}">{}</a>', url, obj.categorie.nom)
    categorie_link.short_description = 'Catégorie'

class BudgetMensuelAdmin(admin.ModelAdmin):
    list_display = ('mois', 'utilisateur_link', 'montant_total_formatted')
    list_filter = ('mois',)
    search_fields = ('utilisateur__username',)
    
    def montant_total_formatted(self, obj):
        return f"{obj.montant_total:.2f} €"
    montant_total_formatted.short_description = 'Budget'
    
    def utilisateur_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.utilisateur.id])
        return format_html('<a href="{}">{}</a>', url, obj.utilisateur.username)
    utilisateur_link.short_description = 'Utilisateur'

class AgentAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'role_badge', 'service', 'last_login')
    list_filter = ('role', 'service')
    search_fields = ('user__username', 'service')
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Utilisateur'
    
    def role_badge(self, obj):
        colors = {
            'ADMIN': 'red',
            'AGENT': 'blue',
            'AUTRE': 'gray'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 10px;">{}</span>',
            colors.get(obj.role, 'gray'),
            obj.get_role_display()
        )
    role_badge.short_description = 'Rôle'
    
    def last_login(self, obj):
        return obj.user.last_login
    last_login.short_description = 'Dernière connexion'

admin.site.register(Agent, AgentAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(BudgetMensuel, BudgetMensuelAdmin)

admin.site.site_header = "Administration FinancialFlow"
admin.site.site_title = "Portail d'administration"
admin.site.index_title = "Gestion de l'application"