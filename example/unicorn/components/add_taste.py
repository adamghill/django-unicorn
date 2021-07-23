from django_unicorn.components import UnicornView
from example.coffee.models import Taste


class AddTasteView(UnicornView):
    # inizializzazione variabili
    # id del taste
    taste_id = None
    # quantità di taste da aggiungere
    taste_qty = 1
    # oggetto taste
    taste_obj = None
    # oggetto flavor
    flavor = None
    # se è attivo adding o meno
    is_adding = False

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        # ottiene il taste_id
        self.taste_id = kwargs.get("taste_id")
        # adding è off a caricamento pagina
        self.is_adding = False

    def create_taste(self):
        if int(self.taste_qty) > 0:
            # crea un taste per ogni qty che l'utente ha stabilito
            for i in range(int(self.taste_qty)):
                # trova i taste collegati al flavor della riga
                taste = Taste.objects.create(id=self.taste_id)
                # edita il flavor per impostarne la foreign key alla primary key del taste?
                # non dovrebbe anche generare un taste nuovo con un create() ?
                taste.save()  # salva taste
                print("create taste in flavor")

        # spegne adding
        self.is_adding = False
        # mostra l'elenco dei tastes
        self.show_table()

    def add_taste(self):
        # accende l'adding e mostra tabella
        self.is_adding = True
        self.show_table()

    def cancel_taste(self):
        # spegne adding
        self.is_adding = False
        self.show_table()

    def show_table(self):
        # mostra l'elenco dei tastes collegati al flavor in riga
        self.taste_obj = Taste.objects.filter(flavor=self.taste_id)

    # mostra l'elenco alla creazione del component
    def mount(self):
        self.show_table()
