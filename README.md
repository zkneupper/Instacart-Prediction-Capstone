![tech-stack](reports/images/Instacart_logo_and_wordmark.svg.png)


Predicting Behavior of Instacart Shoppers
==========================================

[Kaggle.com](kaggle.com) recently hosted the Instacart Market Basket Analysis competition.  The goal of this competition was to predict what grocery items Instacart each users will reorder based on the user’s purchase history.

Kazuki Onodera, a data scientist at Yahoo! JAPAN, won second place in the competition.  Onodera was able to take the original dataset and engineer some strongly predictive new features.  

In this project, I engineered a subset of the most important features identified by Onodera.  I trained a gradient boosting model to predict whether a user will reorder an item that they previously ordered.  I also performed a grid search to find an optimal decision threshold so as to maximize the F1 score of our predictive model.

I was able to to achieve a mean best cross-validated F1 score of 0.12 and a mean cross-validated ROC AUC score 0.79.

------------

Keywords:  Consumer behavior; Machine learning; Gradient boosting; XGBoost

------------


## Table of Contents

[Process Overview and Tech Stack](#process-overview-and-tech-stack)   
[Final Report](#final-report)   
[GitHub Folder Structure](#github-folder-structure)  
[References](#references)  
[Acknowledgements](#acknowledgements)

------------

## Process Overview and Tech Stack

![tech-stack](reports/images/tech-stack.png)

------------

## Final Report

The final report for the project can be found [here](https://github.com/zkneupper/Instacart-Prediction-Capstone/tree/master/reports/Final_Report.pdf).

------------

## GitHub Folder Structure

    ├── LICENSE
    ├── README.md          <- The top-level README for this project.
    ├── data
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── models             <- Trained and serialized models
    │
    ├── notebooks          <- Jupyter notebooks.
    │
    ├── references         <- Dataset descriptions.
    │
    ├── reports            <- Generated analysis as PDF reports and Jupyter notebooks.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │   └── images    
    │
    └── src                <- Source code for use in this project.
        ├── __init__.py    <- Makes src a Python module
        │  
        ├── data           <- Scripts to download or generate data
        │   └── make_dataset.py
        │
        ├── features       <- Scripts to turn raw data into features for modeling
        │   └── build_features.py
        │
        └── models         <- Scripts to train models and then use trained models to make
            │                 predictions
            ├── predict_model.py
            └── train_model.py

------------

## References

1. [“The Instacart Online Grocery Shopping Dataset 2017”](https://www.instacart.com/datasets/grocery-shopping-2017), accessed on June 25, 2017.

2. [Instacart Market Basket Analysis](https://www.kaggle.com/c/instacart-market-basket-analysis#description) challenge on www.kaggle.com.

3. ["Instacart Market Basket Analysis, Winner's Interview: 2nd place, Kazuki Onodera"](http://blog.kaggle.com/2017/09/21/instacart-market-basket-analysis-winners-interview-2nd-place-kazuki-onodera/) by Edwin Chen, dated September 21, 2017.


------------

## Acknowledgements

This was one of my capstone projects for the Data Science Career Track program at [Springboard](https://www.springboard.com/workshops/data-science-career-track).  

I would like to thank my mentor Kenneth Gil-Pasquel for his guidance and feedback.  

------------
