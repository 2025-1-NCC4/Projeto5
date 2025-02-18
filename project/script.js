// Mock exchange rates (in production, these would come from an API)
const exchangeRates = {
    USD: {
        EUR: 0.92,
        BRL: 5.04,
        THB: 35.2,
        VND: 24450
    },
    EUR: {
        USD: 1.09,
        BRL: 5.48,
        THB: 38.3,
        VND: 26650
    },
    BRL: {
        USD: 0.20,
        EUR: 0.18,
        THB: 7.0,
        VND: 4850
    }
};

// DOM Elements
const amountInput = document.getElementById('amount');
const fromCurrency = document.getElementById('from-currency');
const toCurrency = document.getElementById('to-currency');
const swapButton = document.getElementById('swap-currencies');
const convertButton = document.getElementById('convert');
const resultDiv = document.getElementById('result');

// Event Listeners
swapButton.addEventListener('click', () => {
    const temp = fromCurrency.value;
    fromCurrency.value = toCurrency.value;
    toCurrency.value = temp;
    if (amountInput.value) {
        convertCurrency();
    }
});

convertButton.addEventListener('click', convertCurrency);

amountInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        convertCurrency();
    }
});

// Currency Conversion Function
function convertCurrency() {
    const amount = parseFloat(amountInput.value);
    const from = fromCurrency.value;
    const to = toCurrency.value;

    if (isNaN(amount)) {
        resultDiv.innerHTML = '<span style="color: #ef4444;">Por favor, digite um valor válido</span>';
        return;
    }

    const rate = exchangeRates[from][to] || 1 / exchangeRates[to][from];
    const result = amount * rate;

    resultDiv.innerHTML = `
        <span class="font-semibold">${amount.toFixed(2)} ${from}</span>
        =
        <span class="font-semibold">${result.toFixed(2)} ${to}</span>
    `;
}

// Smooth Scroll for Navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add animation to destination cards on scroll
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.destination-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(card);
});