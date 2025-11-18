class Calculator {
    constructor(previousOperandElement, currentOperandElement) {
        this.previousOperandElement = previousOperandElement;
        this.currentOperandElement = currentOperandElement;
        this.clear();
    }

    clear() {
        this.currentOperand = '0';
        this.previousOperand = '';
        this.operation = undefined;
        this.shouldResetDisplay = false;
    }

    delete() {
        if (this.shouldResetDisplay) return;
        
        if (this.currentOperand === '0') return;
        
        if (this.currentOperand.length === 1) {
            this.currentOperand = '0';
        } else {
            this.currentOperand = this.currentOperand.slice(0, -1);
        }
    }

    appendNumber(number) {
        if (number === '.' && this.currentOperand.includes('.')) return;
        
        if (this.shouldResetDisplay || this.currentOperand === '0') {
            if (number === '.') {
                this.currentOperand = '0.';
            } else {
                this.currentOperand = number;
            }
            this.shouldResetDisplay = false;
        } else {
            this.currentOperand += number;
        }
    }

    chooseOperation(operation) {
        if (this.currentOperand === '0' && this.previousOperand === '') return;
        
        if (this.previousOperand !== '') {
            this.compute();
        }
        
        this.operation = operation;
        this.previousOperand = this.currentOperand;
        this.shouldResetDisplay = true;
    }

    compute() {
        let computation;
        const prev = parseFloat(this.previousOperand);
        const current = parseFloat(this.currentOperand);
        
        if (isNaN(prev) || isNaN(current)) return;
        
        switch (this.operation) {
            case '+':
                computation = prev + current;
                break;
            case '-':
                computation = prev - current;
                break;
            case '*':
                computation = prev * current;
                break;
            case '/':
                if (current === 0) {
                    this.currentOperand = 'Error';
                    this.previousOperand = '';
                    this.operation = undefined;
                    this.shouldResetDisplay = true;
                    return;
                }
                computation = prev / current;
                break;
            case '%':
                computation = prev % current;
                break;
            default:
                return;
        }
        
        // Round the result to avoid floating point issues
        this.currentOperand = Math.round(computation * 1000000) / 1000000 + '';
        this.operation = undefined;
        this.previousOperand = '';
        this.shouldResetDisplay = true;
    }

    getDisplayNumber(number) {
        if (number === 'Error') return 'Error';
        
        const stringNumber = number.toString();
        const integerDigits = parseFloat(stringNumber.split('.')[0]);
        const decimalDigits = stringNumber.split('.')[1];
        
        let integerDisplay;
        
        if (isNaN(integerDigits)) {
            integerDisplay = '';
        } else {
            integerDisplay = integerDigits.toLocaleString('en', { maximumFractionDigits: 0 });
        }
        
        if (decimalDigits != null) {
            return `${integerDisplay}.${decimalDigits}`;
        } else {
            return integerDisplay;
        }
    }

    updateDisplay() {
        this.currentOperandElement.innerText = this.getDisplayNumber(this.currentOperand);
        if (this.operation != null) {
            // Display operation symbol
            let operationSymbol;
            switch(this.operation) {
                case '+': operationSymbol = '+'; break;
                case '-': operationSymbol = '−'; break;
                case '*': operationSymbol = '×'; break;
                case '/': operationSymbol = '÷'; break;
                case '%': operationSymbol = '%'; break;
                default: operationSymbol = this.operation;
            }
            this.previousOperandElement.innerText = 
                `${this.getDisplayNumber(this.previousOperand)} ${operationSymbol}`;
        } else {
            this.previousOperandElement.innerText = '';
        }
    }
}

// DOM Elements
const numberButtons = document.querySelectorAll('[data-number]');
const operationButtons = document.querySelectorAll('[data-operator]');
const equalsButton = document.getElementById('equals');
const deleteButton = document.getElementById('delete');
const clearButton = document.getElementById('clear');
const previousOperandElement = document.getElementById('previous-operand');
const currentOperandElement = document.getElementById('current-operand');

// Initialize Calculator
const calculator = new Calculator(previousOperandElement, currentOperandElement);

// Event Listeners
numberButtons.forEach(button => {
    button.addEventListener('click', () => {
        calculator.appendNumber(button.getAttribute('data-number'));
        calculator.updateDisplay();
    });
});

operationButtons.forEach(button => {
    button.addEventListener('click', () => {
        calculator.chooseOperation(button.getAttribute('data-operator'));
        calculator.updateDisplay();
    });
});

equalsButton.addEventListener('click', () => {
    calculator.compute();
    calculator.updateDisplay();
});

clearButton.addEventListener('click', () => {
    calculator.clear();
    calculator.updateDisplay();
});

deleteButton.addEventListener('click', () => {
    calculator.delete();
    calculator.updateDisplay();
});

// Keyboard support
document.addEventListener('keydown', (event) => {
    if (event.key >= '0' && event.key <= '9' || event.key === '.') {
        calculator.appendNumber(event.key);
        calculator.updateDisplay();
    } else if (event.key === '+' || event.key === '-' || event.key === '*' || event.key === '/' || event.key === '%') {
        calculator.chooseOperation(event.key);
        calculator.updateDisplay();
    } else if (event.key === 'Enter' || event.key === '=') {
        event.preventDefault();
        calculator.compute();
        calculator.updateDisplay();
    } else if (event.key === 'Backspace') {
        calculator.delete();
        calculator.updateDisplay();
    } else if (event.key === 'Escape' || event.key === 'Delete') {
        calculator.clear();
        calculator.updateDisplay();
    }
});