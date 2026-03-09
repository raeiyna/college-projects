const display = document.getElementById("display");

function appendChar(char) {
  display.value += char;
}

function clearDisplay() {
  display.value = "";
}

function calculateResult() {
  try {
    const expr = display.value.trim();
    if (!expr) return;
    const result = eval(expr);
    display.value = result;
  } catch {
    display.value = "Syntax Error";
  }
}
