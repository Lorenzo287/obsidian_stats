import numpy as np
import matplotlib.pyplot as plt

def sleep_bonus_function(sleep_minutes):
    """Applies an asymmetric Gaussian-like function for sleep impact."""
    A = 8 # Maximum sleep bonus
    mu = 480      # Ideal sleep duration (8 hours)
    sigma_under = 120    # Stricter penalty for undersleeping
    sigma_over = 200    # Gentler penalty for oversleeping

    # Use different sigma values for under- vs over-sleep
    sigma = sigma_under if sleep_minutes <= mu else sigma_over

    return A * np.exp(-((sleep_minutes - mu) ** 2) / (2 * sigma ** 2))

# Same plotting code
sleep_minutes = np.linspace(300, 720, 100)  # Range: 5h to 12h
sleep_scores = [sleep_bonus_function(x) for x in sleep_minutes]

plt.figure(figsize=(8, 4))
plt.plot(sleep_minutes, sleep_scores, label="Sleep Bonus")
plt.axvline(480, color='r', linestyle='--', label="Optimal Sleep (8h)")
plt.axvline(360, color='gray', linestyle='dotted', label="6h Threshold")
plt.axvline(600, color='gray', linestyle='dotted', label="10h Threshold")
plt.xlabel("Sleep Minutes")
plt.ylabel("Bonus Points")
plt.title("Impact of Sleep on Productivity Score")
plt.legend()
plt.grid()
plt.show()
