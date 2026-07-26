import os
import json
import numpy as np

# Dataset definition across 7 technical categories
CATEGORIES = [
    "Artificial Intelligence",
    "Machine Learning",
    "Computer Vision",
    "Natural Language Processing",
    "Robotics",
    "Cyber Security",
    "Cloud Computing"
]

TRAINING_DATA = [
    # Artificial Intelligence
    ("Artificial intelligence systems leverage search algorithms, knowledge representation, reasoning, planning, and expert systems to solve complex problems.", "Artificial Intelligence"),
    ("Symbolic AI, logic programming, multi-agent coordination, heuristic search, and automated decision making form the foundation of classical AI systems.", "Artificial Intelligence"),
    ("AGI or artificial general intelligence research focuses on cognitive architectures, transfer learning, and autonomous reasoning across multiple domains.", "Artificial Intelligence"),
    ("Heuristic search graphs, A* algorithms, constraint satisfaction problems, and knowledge bases drive automated planning in artificial intelligence.", "Artificial Intelligence"),
    
    # Machine Learning
    ("Supervised learning algorithms including linear regression, decision trees, random forests, and gradient boosting predict outcomes from labeled data.", "Machine Learning"),
    ("Unsupervised clustering like K-means, DBSCAN, and principal component analysis (PCA) discover hidden structures in unlabelled datasets.", "Machine Learning"),
    ("Deep neural networks, backpropagation, stochastic gradient descent, hyperparameter tuning, and overfitting regularization optimize loss functions.", "Machine Learning"),
    ("Reinforcement learning agents optimize policy gradients and Q-learning rewards in Markov decision process environments.", "Machine Learning"),
    
    # Computer Vision
    ("Convolutional neural networks (CNNs), ResNet architectures, image segmentation, object detection, and feature extraction process visual data.", "Computer Vision"),
    ("YOLO v8, Faster R-CNN, bounding box classification, optical flow, and image classification identify targets in real-time camera streams.", "Computer Vision"),
    ("Visual SLAM, 3D reconstruction, point cloud processing, image registration, and stereo vision reconstruct physical environments from images.", "Computer Vision"),
    ("Generative adversarial networks (GANs) and diffusion models synthesize high-resolution photorealistic images and video sequences.", "Computer Vision"),
    
    # Natural Language Processing
    ("Transformers, attention mechanisms, BERT, GPT-4, sequence-to-sequence models, and tokenization enable advanced natural language understanding.", "Natural Language Processing"),
    ("Named entity recognition (NER), part-of-speech tagging, sentiment analysis, text classification, and dependency parsing analyze unstructured text.", "Natural Language Processing"),
    ("Word embeddings like Word2Vec, GloVe, and contextual embeddings capture semantic vector representations of words and sentences.", "Natural Language Processing"),
    ("Machine translation, language modeling, document summarization, and question answering systems process human speech and written corpus.", "Natural Language Processing"),
    
    # Robotics
    ("Kinematics, dynamics, actuator control, robotic arms, inverse kinematics, and PID controllers govern physical robot manipulation.", "Robotics"),
    ("Autonomous mobile robots (AMRs), LiDAR navigation, path planning algorithms, trajectory generation, and obstacle avoidance explore terrain.", "Robotics"),
    ("Humanoid robotics, soft robotics, tactile sensors, haptic feedback, and motor torque control enable precise dexterous interaction.", "Robotics"),
    ("ROS (Robot Operating System), Gazebo simulation, joint trajectory controllers, and sensor fusion integrate robotic hardware and software.", "Robotics"),
    
    # Cyber Security
    ("Cryptographic encryption algorithms like AES-256, RSA, public key infrastructure (PKI), zero trust architecture, and digital signatures secure data.", "Cyber Security"),
    ("Penetration testing, vulnerability assessments, intrusion detection systems (IDS), firewalls, and malware analysis defend against cyber threats.", "Cyber Security"),
    ("Phishing protection, endpoint detection and response (EDR), denial of service (DoS) mitigation, and threat intelligence analyze security logs.", "Cyber Security"),
    ("Identity and access management (IAM), multi-factor authentication (MFA), vulnerability exploits, and SIEM security logging prevent unauthorized access.", "Cyber Security"),
    
    # Cloud Computing
    ("Microservices, Kubernetes orchestration, Docker containers, serverless computing, and AWS/Azure cloud infrastructure scale enterprise apps.", "Cloud Computing"),
    ("Infrastructure as Code (IaC) using Terraform, cloud load balancing, auto-scaling groups, and virtual private clouds (VPC) manage deployment.", "Cloud Computing"),
    ("Cloud storage buckets, serverless Lambda functions, API Gateways, multi-region database replication, and DevOps CI/CD pipelines run applications.", "Cloud Computing"),
    ("Distributed systems, cloud resilience, elasticity, high availability clusters, container runtimes, and service mesh manage cloud traffic.", "Cloud Computing")
]

# Expand dataset with realistic variations
def expand_dataset(data, multiplier=10):
    expanded = []
    for text, cat in data:
        words = text.split()
        for i in range(multiplier):
            # Create synthetic variations by shuffling phrase order or sub-sampling
            np.random.seed(i * 37 + len(words))
            shuffled_words = list(words)
            np.random.shuffle(shuffled_words)
            variant_text = f"{text} {' '.join(shuffled_words[:len(words)//2])}"
            expanded.append((variant_text, cat))
    return expanded

def main():
    print("Preparing training dataset...")
    raw_dataset = expand_dataset(TRAINING_DATA, multiplier=25)
    texts = [item[0] for item in raw_dataset]
    labels = [item[1] for item in raw_dataset]

    label_to_idx = {cat: i for i, cat in enumerate(CATEGORIES)}
    idx_to_label = {i: cat for i, cat in enumerate(CATEGORIES)}
    y_indices = np.array([label_to_idx[lbl] for lbl in labels])

    output_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "models")
    os.makedirs(output_dir, exist_ok=True)

    # Save label mapping
    with open(os.path.join(output_dir, "labels.json"), "w") as f:
        json.dump({"categories": CATEGORIES, "label_to_idx": label_to_idx, "idx_to_label": idx_to_label}, f, indent=2)

    try:
        import tensorflow as tf
        from tensorflow.keras import layers, models

        print(f"TensorFlow Version: {tf.__version__}")
        print(f"Training on {len(texts)} samples across {len(CATEGORIES)} categories...")

        # Feature engineering via TextVectorization
        max_tokens = 2000
        seq_length = 200
        
        vectorize_layer = layers.TextVectorization(
            max_tokens=max_tokens,
            output_mode='int',
            output_sequence_length=seq_length
        )
        vectorize_layer.adapt(texts)

        # Build Neural Network
        model = models.Sequential([
            vectorize_layer,
            layers.Embedding(input_dim=max_tokens, output_dim=32, input_length=seq_length),
            layers.GlobalAveragePooling1D(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dense(len(CATEGORIES), activation='softmax')
        ])

        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

        model.fit(np.array(texts), y_indices, epochs=25, batch_size=16, verbose=1)

        model_path = os.path.join(output_dir, "tf_doc_classifier.keras")
        model.save(model_path)
        print(f"TensorFlow model successfully trained and saved to: {model_path}")

    except Exception as e:
        print(f"TensorFlow training notice: {e}")
        print("Creating lightweight Scikit-Learn TF-IDF + MLP fallback classifier model...")
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.neural_network import MLPClassifier
        import joblib

        vec = TfidfVectorizer(max_features=2000)
        X = vec.fit_transform(texts).toarray()
        clf = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42)
        clf.fit(X, y_indices)

        joblib.dump(vec, os.path.join(output_dir, "tfidf_vec.joblib"))
        joblib.dump(clf, os.path.join(output_dir, "mlp_clf.joblib"))
        print(f"Fallback TF-IDF MLP classifier saved to: {output_dir}")

if __name__ == "__main__":
    main()
