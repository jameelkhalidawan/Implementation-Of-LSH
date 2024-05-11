import numpy as np
from itertools import combinations

def create_shingles(doc, k_values=[2, 5, 10]):
    shingles = {}
    for k in k_values:
        shingles[k] = set()
        with open(doc, 'r', encoding='utf-8') as file:
            text = file.read()
            for i in range(len(text) - k + 1):
                shingle = text[i:i+k]
                shingles[k].add(shingle)
    return shingles

def create_vocabulary(shingles_list):
    vocabulary = set()
    for shingles in shingles_list:
        for k, shingle_set in shingles.items():
            vocabulary.update(shingle_set)
    return vocabulary

def transform_to_vector(shingles, vocabulary):
    vector = [1 if shingle in shingles else 0 for shingle in vocabulary]
    return vector

def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

def minhash_signature(vector, hash_functions):
    signature = [min([hash_func[i] for i, x in enumerate(vector) if x]) for hash_func in hash_functions]
    return signature

class LSH:
    def __init__(self, b):
        self.b = b
        self.buckets = []
        self.counter = 0
        for _ in range(b):
            self.buckets.append({})

    def make_subvecs(self, signature):
        l = len(signature)
        assert l % self.b == 0
        r = int(l / self.b)
        # break signature into subvectors
        subvecs = []
        for i in range(0, l, r):
            subvecs.append(signature[i:i + r])
        return np.stack(subvecs)

    def add_hash(self, signature):
        subvecs = self.make_subvecs(signature).astype(str)
        for i, subvec in enumerate(subvecs):
            subvec = ','.join(subvec)
            if subvec not in self.buckets[i].keys():
                self.buckets[i][subvec] = []
            self.buckets[i][subvec].append(self.counter)
        self.counter += 1

    def check_candidates(self):
        candidates = []
        for bucket_band in self.buckets:
            keys = bucket_band.keys()
            for bucket in keys:
                hits = bucket_band[bucket]
                if len(hits) > 1:
                    candidates.extend(combinations(hits, 2))
        return set(candidates),print(set(candidates))

documents = ["D1.txt", "D2.txt", "D3.txt"]

def user_interface(documents):
    while True:
        shingles_list = []
        vocabulary = set()

        doc_choice = input("\n\nEnter the document numbers to compare (e.g., '1 2'): ")
        doc_choice = list(map(int, doc_choice.split()))

        k = int(input("Enter the value of k (2, 5, or 10): "))
        threshold = float(input("Enter the threshold value (between 0.2 and 0.9): "))

        shingles_list = [create_shingles(doc, [k]) for doc in documents]

        #Combine Shingles to Create Vocabulary
        vocabulary = create_vocabulary(shingles_list)

        #Create hash functions for minhashing
        hash_functions = [np.random.permutation(len(vocabulary)) for _ in range(100)]

        #LSH
        lsh = LSH(20)  #b=20

        for doc_index in doc_choice:
            doc_index -= 1
            doc = documents[doc_index]

            for i in range(len(doc_choice)):
                if i == doc_index:
                    continue

                other_doc_index = doc_choice[i] - 1
                other_doc = documents[other_doc_index]

                shingles1 = shingles_list[doc_index][k]
                shingles2 = shingles_list[other_doc_index][k]

                vector1 = transform_to_vector(shingles1, vocabulary)
                vector2 = transform_to_vector(shingles2, vocabulary)

                if i == 0:
                    jaccard_sim = jaccard_similarity(shingles1, shingles2)
                    print(f"Jaccard similarity between {doc} and {other_doc}: {jaccard_sim}")

                sig1 = minhash_signature(vector1, hash_functions)
                sig2 = minhash_signature(vector2, hash_functions)


                lsh.add_hash(sig1)
                lsh.add_hash(sig2)

        #Check LSH similarity
        candidates = lsh.check_candidates()


        if input("Do you want to continue (y/n): ").lower() != 'y':
            break

# Start the user interface
user_interface(documents)
