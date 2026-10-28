export async function checkCity() {
  const require = (condition, message) => {
    if (!condition) throw new Error(message);
  };
  const frame = () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const click = id => {
    const button = document.getElementById(id);
    require(button, `Missing control: ${id}`);
    button.click();
  };
  const control = (label, value) => {
    const group = Array.from(document.querySelectorAll("#airbar .ag")).find(element => element.querySelector(".eyebrow")?.textContent === label);
    const button = Array.from(group?.querySelectorAll("button") || []).find(element => element.textContent === value);
    require(button, `Missing airport option: ${label} ${value}`);
    button.click();
  };
  const objects = name => {
    const found = [];
    window.__t.scene.traverse(object => { if (object.name === name) found.push(object); });
    return found;
  };
  require(window.__ready, "Wait for the city to load before running checks.");
  require(document.getElementById("underground"), "Underground must be a permanent city control.");
  require(window.__air && document.getElementById("airbar"), "Run checks on the synthetic app with ?airport.");
  require(document.querySelector('[data-id="thriving-demo"]'), "Checks require the synthetic demo dataset.");
  const api = window.__t, air = window.__air.AIR;
  const original = {
    id: document.querySelector('#picker [aria-pressed="true"]').dataset.id,
    areas: { ...air.areas }, containers: air.cont, variant: air.variant,
    under: document.getElementById("underground").getAttribute("aria-pressed") === "true",
    target: api.view.target.clone(), zoom: api.view.zoom, az: api.view.az
  };
  const checks = [];
  let blob = null;
  const createURL = URL.createObjectURL;
  try {
    api.choose("thriving-demo", false);
    control("Presets", "Everything L3");
    control("Compose", "1");
    const visibleAreas = new Set();
    api.scene.traverse(object => {
      if (object.userData.pick?.kind?.startsWith("AIR:gate:")) visibleAreas.add(object.userData.pick.kind);
    });
    for (const key of ["terraform", "compose", "dockerfile", "devcontainer", "agent", "cross"]) {
      require(visibleAreas.has("AIR:gate:" + key), `Applicable airport area is hidden at L1: ${key}`);
    }
    checks.push("All applicable areas remain visible independently of stand capacity");
    for (const [label, key] of [["Agent guidance \u00b7 repo-wide", "agent"], ["Cross-cutting \u00b7 repo-wide", "cross"]]) {
      const appearances = new Set();
      for (const level of [0, 1, 2, 3]) {
        control(label, String(level));
        const marker = objects("airport-area-" + key)[0];
        require(marker, `Missing independent ${key} display at L${level}`);
        if (key === "agent") require(objects("airport-support-agent").length === 1, `Missing guidance office at L${level}`);
        const meshes = [];
        marker.traverse(object => {
          if (object.isMesh) meshes.push([object.position.toArray(), object.geometry.parameters,
            (Array.isArray(object.material) ? object.material : [object.material]).map(material => material.color?.getHex())]);
        });
        appearances.add(JSON.stringify(meshes));
        require(objects("airport-small-terminal").length === 1, `${key} changed overall airport level`);
      }
      require(appearances.size === 4, `${key} must visibly change at every level`);
    }
    control("Presets", "Everything L3");
    control("Compose", "2");
    const width = objects("airport-terminal")[0].children[0].geometry.parameters.width;
    for (const value of ["\u2013", "0", "1", "2", "3"]) {
      control("Devcontainer", value);
      require(document.getElementById("airportLevel").textContent.includes("Airport L2"), `Devcontainer ${value} downgraded the core airport`);
      require(objects("airport-terminal").length === 1, `Devcontainer ${value} removed the core terminal`);
      require(objects("airport-small-terminal").length === 0, `Devcontainer ${value} downgraded the core terminal`);
      if (value !== "\u2013") require(objects("airport-area-devcontainer").length === 1, `Devcontainer ${value}: area display disappeared`);
      require(objects("airport-support-devcontainer").length === (value === "\u2013" ? 0 : 1), `Devcontainer ${value}: incorrect optional side-terminal`);
      require(objects("airport-terminal")[0].children[0].geometry.parameters.width === width, "Adding Devcontainer reshaped the core terminal");
      require(!document.getElementById("airportLevel").textContent.includes("Devcontainer"), "Devcontainer must not be a limiting core area");
    }
    control("Presets", "No infrastructure");
    control("Devcontainer", "3");
    control("Agent guidance \u00b7 repo-wide", "2");
    require(objects("airport-support-devcontainer").length === 1 && objects("airport-support-agent").length === 1, "Support-only facilities must remain visible");
    require(objects("airport-terminal").length === 0 && objects("airport-hangar").length === 0, "Support-only areas invented a core airport");
    const airportMetro = objects("metro-train").filter(object => object.userData.pick?.kind === "AIR:link");
    require(airportMetro.length === 0, "Support-only areas invented airport transport service");
    checks.push("Devcontainer and guidance are independent, non-blocking support facilities");
    control("Presets", "n8n-like (Compose + Docker)");
    click("surface");
    for (const level of [0, 1, 2, 3, 1, 2]) {
      control("Compose", String(level));
      control("Dockerfile", String(level));
      require(!!objects("airport-hangar").length === (level > 0), `Hangar at L${level}`);
      require(!!objects("airport-small-terminal").length === (level === 1), `Small airfield at L${level}`);
      require(!!objects("airport-terminal").length === (level >= 2), `Regional terminal at L${level}`);
      const metro = objects("metro-train").filter(object => object.userData.pick?.kind === "AIR:link");
      require(!!metro.length === (level >= 2), `Airport metro must start at L2, not L${level}`);
    }
    checks.push("L0-L3 airport buildings and metro threshold");
    click("underground");
    const materialState = () => {
      const state = [];
      api.scene.traverse(object => {
        if (!object.isMesh) return;
        for (const material of (Array.isArray(object.material) ? object.material : [object.material])) {
          if (!material.isMeshBasicMaterial) state.push([material.opacity, material.transparent, material.depthWrite]);
        }
      });
      return JSON.stringify(state);
    };
    const before = materialState(), allocations = [];
    for (let iteration = 0; iteration < 6; iteration++) {
      control("Compose", "1");
      control("Compose", "2");
      await frame();
      allocations.push(api.renderer.info.memory.geometries);
      require(materialState() === before, "Rebuild changed original material opacity or depth state.");
    }
    require(allocations[5] === allocations[2], `GPU geometry leak: ${allocations.join(", ")}`);
    control("Station link", "A Same network");
    require(document.getElementById("stage").classList.contains("under"), "Airport variant reset the permanent layer.");
    checks.push("Repeated rebuilds preserve materials, layer and GPU allocation");
    for (const [id, level, metros, buses] of [["thriving-demo", 3, 7, 14], ["prosperous-demo", 2, 7, 14], ["working-demo", 2, 2, 9], ["absent-demo", 0, 0, 0]]) {
      api.choose(id, false);
      require(objects(`central-station-L${level}`).length === 1, `Missing central station in ${id}`);
      require(document.getElementById("stage").classList.contains("under"), "Changing city reset underground view.");
      require(document.getElementById("panel").textContent.includes(`Link to the central station: L${Math.min(level, 2)}`), `Stale airport description in ${id}`);
      require(objects("metro-train").length === metros, `Incorrect metro service in ${id}`);
      require(objects("bus").length === buses, `Incorrect bus service in ${id}`);
    }
    checks.push("Central station at every tier; low-level transport stays honest");
    api.choose("thriving-demo", false);
    api.select(null, "AIR");
    URL.createObjectURL = function(value) {
      if (value.type === "image/png") blob = value;
      return createURL.call(this, value);
    };
    const target = api.view.target.toArray().join(","), zoom = api.view.zoom;
    click("exportPNG");
    while (document.getElementById("exportPNG").disabled) await frame();
    require(blob && document.getElementById("exportStatus").textContent === "PNG exported.", "PNG download failed.");
    const bitmap = await createImageBitmap(blob), canvas = document.createElement("canvas");
    canvas.width = bitmap.width; canvas.height = bitmap.height;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    context.drawImage(bitmap, 0, 0); bitmap.close();
    const pixels = context.getImageData(32, 32, Math.min(800, canvas.width - 64), 400).data;
    const colors = new Set();
    for (let index = 0; index < pixels.length; index += 388) colors.add(pixels.slice(index, index + 4).join(","));
    require(colors.size > 20, "Exported city canvas is blank.");
    require(api.view.target.toArray().join(",") === target && api.view.zoom === zoom, "PNG export changed the live camera.");
    checks.push(`Nonblank PNG with description: ${canvas.width} x ${canvas.height}, ${blob.size} bytes`);
    return { passed: checks, allocations };
  } finally {
    URL.createObjectURL = createURL;
    Object.assign(air.areas, original.areas); air.cont = original.containers; air.variant = original.variant;
    api.choose(original.id, false);
    click(original.under ? "underground" : "surface");
    api.view.target.copy(original.target); api.view.zoom = original.zoom; api.view.az = original.az; api.placeCamera();
    window.__airDraw();
  }
}