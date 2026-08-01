(() => {
  const preset = document.getElementById("preset");
  if (!preset) return;

  const size = document.getElementById("ga_size");
  const pop = document.getElementById("ga_pop");
  const gens = document.getElementById("ga_gens");
  const k = document.getElementById("ga_k");
  const elite = document.getElementById("ga_elite");
  const mut = document.getElementById("ga_mut");

  const applyPreset = (name) => {
    if (!size || !pop || !gens || !k || !elite || !mut) return;

    if (name === "fast") {
      size.value = 21;
      pop.value = 20;
      gens.value = 20;
      k.value = 3;
      elite.value = 2;
      mut.value = 0.30;
    } else if (name === "quality") {
      size.value = 41;
      pop.value = 70;
      gens.value = 90;
      k.value = 4;
      elite.value = 3;
      mut.value = 0.22;
    } else {
      // balanced
      size.value = 31;
      pop.value = 40;
      gens.value = 50;
      k.value = 3;
      elite.value = 2;
      mut.value = 0.25;
    }
  };

  preset.addEventListener("change", (e) => applyPreset(e.target.value));
})();
