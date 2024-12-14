let lightOn = false;

// Toggle Light On/Off
function toggleLight() {
  lightOn = !lightOn;
  document.getElementById("toggleLight").textContent = lightOn ? "Turn Light Off" : "Turn Light On";
}

// Update Color based on RGB sliders
function updateColor() {
  const red = document.getElementById("redSlider").value;
  const green = document.getElementById("greenSlider").value;
  const blue = document.getElementById("blueSlider").value;

  document.getElementById("redValue").value = red;
  document.getElementById("greenValue").value = green;
  document.getElementById("blueValue").value = blue;

  const colorDisplay = document.getElementById("colorDisplay");
  colorDisplay.style.backgroundColor = `rgb(${red}, ${green}, ${blue})`;
}

// Sync Sliders and Input Boxes
function syncSlider(color) {
  const slider = document.getElementById(`${color}Slider`);
  const valueBox = document.getElementById(`${color}Value`);
  slider.value = valueBox.value;
  updateColor();
}

// Pick color from color picker
function pickColor() {
  const colorPicker = document.getElementById("colorPicker").value;
  const r = parseInt(colorPicker.substr(1, 2), 16);
  const g = parseInt(colorPicker.substr(3, 2), 16);
  const b = parseInt(colorPicker.substr(5, 2), 16);

  document.getElementById("redSlider").value = r;
  document.getElementById("greenSlider").value = g;
  document.getElementById("blueSlider").value = b;

  document.getElementById("redValue").value = r;
  document.getElementById("greenValue").value = g;
  document.getElementById("blueValue").value = b;

  updateColor();
}
