import pytest
from app.services.classifier_service import classifier_service

def test_classifier_predict_categories():
    sample_text = "Convolutional neural networks (CNNs), YOLO object detection, and visual feature extraction process camera image frames."
    category, confidence, probs = classifier_service.classify_text(sample_text)

    assert category in classifier_service.categories
    assert 0.0 <= confidence <= 1.0
    assert len(probs) == len(classifier_service.categories)
    assert category == "Computer Vision"

def test_classifier_cyber_security():
    sample_text = "Public Key Infrastructure (PKI), AES-256 encryption, zero trust architecture, and penetration testing defend systems against cyber attacks."
    category, confidence, probs = classifier_service.classify_text(sample_text)

    assert category == "Cyber Security"
    assert confidence > 0.0
