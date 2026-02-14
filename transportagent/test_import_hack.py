
try:
    from . import prediction_engine
    print("Relative import worked")
except ImportError:
    print("Relative import failed, trying absolute")
    import prediction_engine
    print("Absolute import worked")
