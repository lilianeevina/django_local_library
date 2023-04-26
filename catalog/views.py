from .models import Book, Author, BookInstance, Genre
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author
from catalog.forms import RenewBookForm



def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    #available genre = drama
    #num_books_drama = Book.objects.filter(genre__icontains='drama').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    #number of visits to this view, as counted in the session variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits +1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits' : num_visits,
        #'num_books_drama' : num_books_drama,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):

    model = Book

    paginate_by = 10

    context_object_name = 'book_list'   # your own name for the list as a template variable
    template_name = 'catalog/templates/base_generic.html'  # Specify your own template name/location

    def get_queryset(self):
        return Book.objects.all()
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context
    


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'

    template_name = 'catalog/templates/base_generic.html'

    def get_queryset(self):
        return Author.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        context["some_data"] = 'This is just some data'
        return context
    

class AuthorDetailView(generic.DetailView):
    model = Author



class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class BorrowedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(status__exact='o')
            .order_by('due_back')
        )

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
  """View function for renewing a specific BookInstance by librarian."""
  book_instance = get_object_or_404(BookInstance, pk=pk)

  # S'il s'agit d'une requête POST, traiter les données du formulaire.
  if request.method == 'POST':

    # Créer une instance de formulaire et la peupler avec des données récupérées dans la requête (liaison) :
    form = RenewBookForm(request.POST)

    # Vérifier que le formulaire est valide :
    if form.is_valid():
      # Traiter les données dans form.cleaned_data tel que requis (ici on les écrit dans le champ de modèle due_back) :
      book_instance.due_back = form.cleaned_data['renewal_date']
      book_instance.save()

      # Rediriger vers une nouvelle URL :
      return HttpResponseRedirect(reverse('all-borrowed'))

  # S'il s'agit d'une requête GET (ou toute autre méthode), créer le formulaire par défaut.
  else:
    proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
    form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

  context = {
    'form': form,
    'book_instance': book_instance,
  }

  return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death' : '11/06/2020'}


class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Non recommandé (problème potentiel de sécurité si on ajoute d'autres champs)


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')