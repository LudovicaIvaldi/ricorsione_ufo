import copy

from database.DAO import DAO
import networkx as nx

from model.sighting import Sighting


class Model:
    def __init__(self):
        self._grafo = nx.DiGraph()
        self._nodes = []
        self._cammino_ottimo = []
        self._score_ottimo = 0

    def get_years(self):
        return DAO.get_years()

    def get_shapes_year(self, year: int):
        return DAO.get_shapes_year(year)

    def create_graph(self, year: int, shape: str):
        self._grafo.clear()
        self._nodes = DAO.get_nodes(year, shape)
        self._grafo.add_nodes_from(self._nodes)

        # calcolo degli edges in modo programmatico
        for i in range(0, len(self._nodes) - 1):
            for j in range(i + 1, len(self._nodes)):
                if self._nodes[i].state == self._nodes[j].state and self._nodes[i].longitude < self._nodes[j].longitude:
                    weight = self._nodes[j].longitude - self._nodes[i].longitude
                    self._grafo.add_edge(self._nodes[i], self._nodes[j], weight= weight)
                elif self._nodes[i].state == self._nodes[j].state and self._nodes[i].longitude > self._nodes[j].longitude:
                    weight = self._nodes[i].longitude - self._nodes[j].longitude
                    self._grafo.add_edge(self._nodes[j], self._nodes[i], weight= weight)

    def get_top_edges(self):
        sorted_edges = sorted(self._grafo.edges(data=True), key=lambda edge: edge[2].get('weight'), reverse=True)
        return sorted_edges[0:5]


    def get_nodes(self):
        return self._grafo.nodes()

    # def get_edges(self):
    #     return list(self._grafo.edges(data=True))

    def get_num_of_nodes(self):
        return self._grafo.number_of_nodes()

    def get_num_of_edges(self):
        return self._grafo.number_of_edges()

    def cammino_ottimo(self):
        self._cammino_ottimo = []
        self._score_ottimo = 0

#ABBIAMO INIZIATO A SCRIVERE DA QUI ----------------------------------------------------------------------
        #Questa è la funzione chiamata nel controlle quando schiacci sul bottone
        #TODO
        #il primo nodo lo metti qui poi far partire la ricorsione
        for node in self._grafo.nodes():
            parziale=[node]
            rimanenti=self.calcola_rimanenti_parziale(parziale)
            self._ricorsione(parziale, rimanenti)

        return self._cammino_ottimo, self._score_ottimo


    def _ricorsione(self,parziale,nodi_rimanenti ):
        #caso terminale
        if len(nodi_rimanenti)==0 :
            punteggio= self.calcola_punteggio(parziale)
            if punteggio>self._score_ottimo:
                self._score_ottimo = punteggio
                self._cammino_ottimo = copy.deepcopy(parziale)
                print(parziale)

        #caso ricorsivo:
        else:
            #per ogni nodo rimanente
            for nodo in nodi_rimanenti:
                #funziona perchè il grafo è fatto senza possibilità che esistano i cicli
                #aggiungere il nodo
                parziale.append(nodo)
                #calcolare i nuovi rimanenti dopo l'aggiunta el nodo (i suoi siccessori)
                nuovi_rimanenti=self.calcola_rimanenti_parziale(parziale)
                #richiamare la ricorsione con parziale esteso e i nuovi_rimanenti
                self._ricorsione(parziale, nuovi_rimanenti)
                #back traking
                parziale.pop()



    def calcola_rimanenti_parziale(self, parziale):
        #la funzione succeccors dato il grafo e dato l'ultimo nodo cosegna tutti i successori del nodo
        nuovi_rimanenti=[]
        #prediamo i nodi successivi
        for i in self._grafo.successors(parziale[-1]):
            # la funzione torna un iteratore -> sopra ci puoi solo iterare ma non ciedere quanto sia lungo
            # metto dentro una lista
            #verifico il vincolo sul mese prima di appendere
            if self.is_vincolo_ok(parziale,i) and self.is_vincolo_durata_ok(parziale,i):
                nuovi_rimanenti.append(i)
        return nuovi_rimanenti

    def is_vincolo_ok(self, parziale, nodo:Sighting):
        mese=nodo.datetime.month
        counter=0
        for i in parziale:
            if i.datetime.month==mese:
                counter+=1
        if counter>=3:
            return False
        else:
            return True

    def is_vincolo_durata_ok(self, parziale, nodo:Sighting):
        return nodo.duration>parziale[-1].duration

    def calcola_punteggio(self, parziale):
        punteggio=0
        #termine fisso
        punteggio += len(parziale)*100
        #termine variabile
        for i in range(1,len(parziale)):
            nodo=parziale[i]
            nodo_precedente=parziale[i-1]
            if nodo.datetime.month==nodo_precedente.datetime.month:
                punteggio+=200
        return punteggio