from django.contrib import admin
from .models import Author, Book, BookInstance

# Register your models here.
#admin.site.register(Book)
#admin.site.register(Genre)
#admin.site.register(BookInstance)
class BookInLine(admin.TabularInline):
    model = Book
    list_display = ('')

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')

    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    inlines = [BookInLine]

class BookInstanceInLine(admin.TabularInline):
    model = BookInstance
    list_display = ('')


# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInLine]





# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'borrower', 'due_back', 'status')

    list_filter = ('status', 'due_back')

    fieldsets = ((None, {'fields': ('book', 'imprint', 'id')}),
                  ('Availability', {'fields': ('status', 'due_back', 'borrower')}))

    
