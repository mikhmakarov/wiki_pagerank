import numpy as np
import scipy.sparse.linalg

from scipy.sparse import csr_matrix
from time import time


def get_pages(filename, output):
    pages = []
    with open(filename) as links:
        for i, l in enumerate(links):
            page = l.split(',')[0]
            if page not in pages:
                pages.append(page)

    with open(output, 'w') as out:
        out.write('\n'.join(pages))


def assign_indexes(filename):
    page_to_ind = {}
    ind_to_page = []

    with open(filename) as pages:
        for i, page in enumerate(pages):
            page_to_ind[page.strip()] = i
            ind_to_page.append(page.strip())

    return page_to_ind, ind_to_page


def create_matrix(filename, page_to_ind, m=0.15):
    n = len(page_to_ind)
    data = []
    row_ind = []
    col_ind = []

    with open(filename) as links:
        for i, l in enumerate(links):
            items = [item.strip() for item in l.split(',')]
            j = page_to_ind[items[0]]
            connections = [page_to_ind[item] for item in items[1:] if item in page_to_ind]

            w = 1 / len(connections)

            for i in connections:
                data.append(w)
                row_ind.append(i)
                col_ind.append(j)

    return csr_matrix((data, (row_ind, col_ind)), shape=(n, n))


def power_method(A, k=10):
    n = A.shape[0]
    x = np.ones(A.shape[0]) * 1 / n

    for _ in range(k):
        new = A @ x
        x = new / np.linalg.norm(new)

    return x


def main():
    page_to_ind, ind_to_page = assign_indexes('pages.txt')
    n = len(page_to_ind)

    A = create_matrix('wiki_links_3.txt', page_to_ind)
    start = time()

    print('started power method')
    vector = power_method(A)
    print('exec time power', round(time() - start, 2))

    vector = abs(vector.reshape(-1))
    top = 50

    sorted_ind = np.argsort(vector)
    for i in range(1, top + 1):
        print(ind_to_page[sorted_ind[-i]], round(vector[sorted_ind[-i]], 3))
    pass


if __name__ == '__main__':
    get_pages('wiki_links_3.txt', 'pages.txt')
    main()
