from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as cosine


# Similarity functions (categorical, text, and list)
def categorical_similarity(value1, value2, weight):
    return (1 if value1 == value2 else 0) * weight


def text_similarity(text1, text2, weight):
    vectorizer = TfidfVectorizer()
    print(text1,'**********', text2)
    if text1 == text2 == "": return weight
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    sim = cosine(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return sim * weight


def jaccard_similarity(list1, list2, weight):
    set1 = set(list1.split(','))
    set2 = set(list2.split(','))
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    if union == 0:
        return 1.0 * weight  # Consider two empty sets as fully similar
    return (intersection / union) * weight


# Product list-based similarities
def color_similarity(product1, product2, weight):
    return jaccard_similarity(product1.colors, product2.colors, weight)


def size_similarity(product1, product2, weight):
    return jaccard_similarity(product1.sizes, product2.sizes, weight)


# Overall similarity calculation for products
def overall_similarity(product1, product2, clothes_info1=None, clothes_info2=None, shoes_info1=None, shoes_info2=None):
    weights = {
        'gender': 0.05, 'category': 0.10, 'product_type': 0.10, 'age_group': 0.05,
        'name': 0.05, 'description': 0.15, 'pattern': 0.05, 'nice_to_know': 0.05,
        'sizes': 0.05, 'colors': 0.05, 'fit': 0.05, 'length': 0.05, 'sleeve_length': 0.05, 'neckline': 0.05,
        'style': 0.05,
        'heel_height': 0.05, 'additional_description': 0.10, 'footwear_style': 0.05
    }

    gender_sim = categorical_similarity(product1.gender, product2.gender, weights['gender'])
    category_sim = categorical_similarity(product1.category, product2.category, weights['category'])
    product_type_sim = categorical_similarity(product1.product_type, product2.product_type, weights['product_type'])
    age_group_sim = categorical_similarity(product1.age_group, product2.age_group, weights['age_group'])

    name_sim = text_similarity(product1.product_name, product2.product_name, weights['name'])
    description_sim = text_similarity(product1.description, product2.description, weights['description'])
    pattern_sim = text_similarity(product1.pattern, product2.pattern, weights['pattern'])
    nice_to_know_sim = text_similarity(product1.nice_to_know, product2.nice_to_know, weights['nice_to_know'])

    color_sim = color_similarity(product1, product2, weights['colors'])
    size_sim = size_similarity(product1, product2, weights['sizes'])

    clothes_sim = 0
    if clothes_info1 and clothes_info2:
        fit_sim = categorical_similarity(clothes_info1.fit, clothes_info2.fit, weights['fit'])
        length_sim = jaccard_similarity(clothes_info1.length, clothes_info2.length, weights['length'])
        sleeve_sim = categorical_similarity(clothes_info1.sleeve_length, clothes_info2.sleeve_length,
                                            weights['sleeve_length'])
        neckline_sim = jaccard_similarity(clothes_info1.neckline, clothes_info2.neckline, weights['neckline'])
        style_sim = jaccard_similarity(clothes_info1.style, clothes_info2.style, weights['style'])
        clothes_sim = fit_sim + length_sim + sleeve_sim + neckline_sim + style_sim

    shoes_sim = 0
    if shoes_info1 and shoes_info2:
        heel_height_sim = categorical_similarity(shoes_info1.heel_height, shoes_info2.heel_height,
                                                 weights['heel_height'])
        additional_description_sim = text_similarity(shoes_info1.additional_description,
                                                     shoes_info2.additional_description,
                                                     weights['additional_description'])
        footwear_style_sim = jaccard_similarity(shoes_info1.footwear_style, shoes_info2.footwear_style,
                                                weights['footwear_style'])
        shoes_sim = heel_height_sim + additional_description_sim + footwear_style_sim

    overall_sim = (gender_sim + category_sim + product_type_sim + age_group_sim +
                   name_sim + description_sim + pattern_sim + nice_to_know_sim +
                   color_sim + size_sim + clothes_sim + shoes_sim)

    return overall_sim


# Recommend similar products
def recommend_similar_products(target_product, all_products, clothes_info=None, shoes_info=None):
    similarities = []
    for product in all_products:
        sim = overall_similarity(target_product, product, clothes_info, shoes_info)
        similarities.append((product, sim))
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [product for product, sim in similarities]


# Recommend products with lower prices
def recommend_lower_priced_products(target_product, all_products):
    lower_priced_products = [product for product in all_products if product.price < target_product.price]
    lower_priced_products.sort(key=lambda product: product.price)
    return lower_priced_products


# Recommend based on text similarity
def merge_product_text(product):
    return f"{product.product_name} {product.description} {product.pattern} {product.nice_to_know}"


def recommend_based_on_text(user_description, all_products):
    product_texts = [merge_product_text(product) for product in all_products]
    all_texts = product_texts + [user_description]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    user_vector = tfidf_matrix[-1:]
    product_vectors = tfidf_matrix[:-1]
    similarities = cosine(product_vectors, user_vector).flatten()
    product_similarity_pairs = list(zip(all_products, similarities))
    product_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
    return [product for product, sim in product_similarity_pairs]


# Recommend based on gender and age range
def recommend_by_gender_and_age(user_gender, user_age, all_products, top_n=10):
    # Sort the products based on whether they match the user's gender and age
    def sorting_key(product):
        gender_match = 1 if product.gender == user_gender else 0
        age_match = 1 if product.first_age <= user_age <= product.last_age else 0
        return (gender_match, age_match, product.price)

    # Sort the products based on the key
    sorted_products = sorted(all_products, key=sorting_key, reverse=True)

    return sorted_products[:top_n]  # Return the top_n products after sorting


# Recommend based on gender and age range
def filter_by_gender_and_age(user_gender, user_age, all_products):
    # Sort the products based on whether they match the user's gender and age
    filtered_products = [product for product in all_products if
                         product.gender == user_gender and product.first_age <= user_age <= product.last_age]
    filtered_products.sort(key=lambda product: product.price)
    return filtered_products
