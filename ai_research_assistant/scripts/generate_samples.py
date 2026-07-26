import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

SAMPLE_PAPERS = [
    {
        "filename": "paper_ai_agent_architectures.pdf",
        "title": "Autonomous AI Agent Architectures: Reasoning, Planning, and Knowledge Representation",
        "category": "Artificial Intelligence",
        "pages": [
            """<b>1. Abstract & Introduction</b><br/><br/>
Modern Artificial Intelligence (AI) systems are transitioning from static input-output mappers to autonomous agents capable of reasoning, long-term planning, and environment interaction. This paper presents an integrated agent architecture combining symbolic knowledge representation with heuristic search algorithms (A*, Monte Carlo Tree Search). We evaluate decision accuracy, goal satisfaction, and plan execution efficiency across dynamic decision environments.<br/><br/>
<b>2. Knowledge Representation & Planning</b><br/><br/>
Knowledge representation relies on description logics and structured graph databases. The planning subsystem utilizes state-space search with admissible heuristics to formulate multi-step action sequences. Multi-agent coordination mechanisms resolve resource conflicts via automated bargaining protocols.""",
            
            """<b>3. Empirical Results & Discussion</b><br/><br/>
Experimental evaluations demonstrate a 34% improvement in plan execution success compared to classical rule-based systems. Memory footprint during heuristic graph expansion remains bounded within O(b^d) limits.<br/><br/>
<b>4. Conclusion</b><br/><br/>
Combining symbolic AI planning with statistical reasoning produces resilient autonomous agents suitable for high-stakes decision-making environments."""
        ]
    },
    {
        "filename": "paper_deep_learning_optimization.pdf",
        "title": "Scalable Machine Learning: Gradient Descent Optimization and Regularization in Deep Networks",
        "category": "Machine Learning",
        "pages": [
            """<b>1. Abstract & Introduction</b><br/><br/>
Supervised and unsupervised Machine Learning models form the foundation of predictive analytics. Stochastic Gradient Descent (SGD), AdamW, and RMSprop optimization techniques are critical for training deep neural networks. In this work, we analyze convergence rates, loss landscape geometry, and hyperparameter tuning strategies across complex empirical datasets.<br/><br/>
<b>2. Loss Functions & Regularization</b><br/><br/>
To prevent overfitting, we enforce L2 weight decay, dropout regularization (p=0.3), and batch normalization layers. Principal Component Analysis (PCA) and K-means clustering are utilized for exploratory feature reduction and unlabelled data partitioning.""",
            
            """<b>3. Experimental Evaluation</b><br/><br/>
Training convergence was measured across 100 epochs. AdamW optimizer achieved a cross-entropy loss of 0.12 with 94.8% test accuracy on multi-class benchmark datasets.<br/><br/>
<b>4. Conclusion</b><br/><br/>
Proper regularization and adaptive learning rate schedulers drastically reduce generalization error in modern deep learning pipelines."""
        ]
    },
    {
        "filename": "paper_yolo_object_detection.pdf",
        "title": "Real-Time Computer Vision: Convolutional Neural Networks and Object Detection with Visual SLAM",
        "category": "Computer Vision",
        "pages": [
            """<b>1. Abstract & Introduction</b><br/><br/>
Computer Vision applications require high-speed image processing and spatial awareness. We propose an optimized Convolutional Neural Network (CNN) architecture based on YOLO v8 for multi-class object detection and Visual Simultaneous Localization and Mapping (Visual SLAM).<br/><br/>
<b>2. Feature Extraction & Bounding Box Regression</b><br/><br/>
The network extracts multi-scale visual features using spatial pyramid pooling. Bounding box coordinates are predicted alongside class confidence scores. Optical flow and point cloud registration enable 3D scene reconstruction from stereo camera feeds.""",
            
            """<b>3. Performance Metrics</b><br/><br/>
The system achieves 62 FPS at 1080p resolution with a mean Average Precision (mAP@0.5) of 88.4%. Real-time performance was verified on edge hardware devices.<br/><br/>
<b>4. Conclusion</b><br/><br/>
Integrated feature pyramids and lightweight convolutions enable embedded computer vision systems for autonomous navigation."""
        ]
    },
    {
        "filename": "paper_transformer_language_models.pdf",
        "title": "Natural Language Processing: Attention Mechanisms, Tokenization, and Contextual Embeddings",
        "category": "Natural Language Processing",
        "pages": [
            """<b>1. Abstract & Introduction</b><br/><br/>
Natural Language Processing (NLP) has been revolutionized by self-attention mechanisms and Transformer architectures. This paper investigates contextual word embeddings (BERT, GPT), subword tokenization (Byte-Pair Encoding), and sequence-to-sequence translation.<br/><br/>
<b>2. Attention Mechanics & Named Entity Recognition</b><br/><br/>
Multi-head attention computes Query, Key, and Value matrix projections to capture long-range linguistic dependencies. Named Entity Recognition (NER) and sentiment classification tasks demonstrate state-of-the-art accuracy when fine-tuned on domain specific text.""",
            
            """<b>3. Results</b><br/><br/>
Fine-tuned Transformer models reached a BLEU score of 41.2 on machine translation and an F1-score of 92.1% on domain specific NER tasks.<br/><br/>
<b>4. Conclusion</b><br/><br/>
Self-attention mechanisms provide superior context modeling compared to traditional recurrent architectures (LSTM/GRU)."""
        ]
    },
    {
        "filename": "paper_cloud_microservices_security.pdf",
        "title": "Cloud Computing Infrastructure: Kubernetes Microservices, Serverless Deployment, and Cyber Security",
        "category": "Cloud Computing",
        "pages": [
            """<b>1. Abstract & Introduction</b><br/><br/>
Modern Cloud Computing infrastructure relies on microservices architecture, Docker containers, and Kubernetes orchestration. Securing cloud environments requires Zero Trust Architecture, Public Key Infrastructure (PKI), AES-256 encryption, and identity management.<br/><br/>
<b>2. Cloud Infrastructure & Security Protocols</b><br/><br/>
Infrastructure as Code (IaC) templates define Virtual Private Clouds (VPC), auto-scaling groups, and API Gateways. Intrusion Detection Systems (IDS) monitor network traffic while SIEM logging aggregates security event telemetry across distributed clusters.""",
            
            """<b>3. Resilience & Security Analysis</b><br/><br/>
Chaos engineering tests validated 99.99% service availability during multi-region failover scenarios. Penetration testing confirmed zero unauthorized access vulnerabilities under simulated DoS attacks.<br/><br/>
<b>4. Conclusion</b><br/><br/>
Combining container orchestration with automated threat detection ensures scalable, resilient, and secure enterprise cloud deployments."""
        ]
    }
]

def generate_pdf(filepath, title, pages):
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        spaceAfter=20
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=12
    )

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 15))

    for idx, page_content in enumerate(pages):
        if idx > 0:
            story.append(PageBreak())
        story.append(Paragraph(page_content, body_style))

    doc.build(story)

def main():
    target_dir = os.path.join(os.path.dirname(__file__), "..", "sample_docs")
    os.makedirs(target_dir, exist_ok=True)

    print(f"Generating realistic sample PDF research documents in: {target_dir}")
    for paper in SAMPLE_PAPERS:
        fp = os.path.join(target_dir, paper["filename"])
        generate_pdf(fp, paper["title"], paper["pages"])
        print(f" -> Generated: {paper['filename']} ({paper['category']})")

if __name__ == "__main__":
    main()
