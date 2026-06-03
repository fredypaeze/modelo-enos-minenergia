const pptxgen = require("pptxgenjs");
const fs = require("fs");

const C = {
  amarillo: "FFC000", gris: "3A3838", blanco: "FFFFFF",
  naranja: "ED7D31", grisLt: "F5F5F5", grisMd: "D9D9D9",
  grisText: "595959", verde: "1A7A4A", azulMd: "1F6B8E",
};
const makeSh = () => ({ type:"outer", blur:6, offset:2, angle:135, color:"000000", opacity:0.10 });
const logoDorado = "image/png;base64," + fs.readFileSync("D:\\Proyectos\\minenergia\\sddp\\assets\\logo_energia.png").toString("base64");function addHeader(slide, pres, t) {
  slide.addShape(pres.shapes.RECTANGLE, { x:0,y:0,w:10,h:0.12, fill:{color:C.amarillo}, line:{color:C.amarillo} });
  slide.addImage({ data:logoDorado, x:9.1,y:0.15,w:0.7,h:0.7 });
  slide.addText(t, { x:0.4,y:0.18,w:8.5,h:0.62, fontSize:20,bold:true,color:C.gris,fontFace:"Arial",margin:0 });
  slide.addShape(pres.shapes.LINE, { x:0.4,y:0.83,w:9.2,h:0, line:{color:C.amarillo,width:1.5} });
}
function addFooter(slide, pres, label) {
  slide.addShape(pres.shapes.RECTANGLE, { x:0,y:5.35,w:10,h:0.28, fill:{color:C.gris}, line:{color:C.gris} });
  slide.addText("Ministerio de Minas y Energía — Subdirección de Análisis y Modelamiento", { x:0.25,y:5.37,w:8.5,h:0.24, fontSize:7.5,color:"AAAAAA",fontFace:"Arial",margin:0 });
  slide.addText(label, { x:9.4,y:5.37,w:0.5,h:0.24, fontSize:7.5,color:"AAAAAA",fontFace:"Arial",align:"right",margin:0 });
}

async function build() {
  let pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";

  // ── SLIDE 1: Aportes históricos + ENOS ──────
  let s1 = pres.addSlide();
  s1.background = { color: C.blanco };
  addHeader(s1, pres, "Evidencia empírica: aportes hídricos 2010–2026 con eventos ENOS");
  addFooter(s1, pres, "D1");

  s1.addShape(pres.shapes.RECTANGLE, { x:0.4,y:0.95,w:9.2,h:0.46, fill:{color:C.gris},line:{color:C.gris} });
  s1.addText("Datos reales XM — Sistema eléctrico colombiano. Zonas amarillas = eventos El Niño confirmados (2010, 2015-2016, 2023-2024).", {
    x:0.55,y:0.97,w:8.8,h:0.42, fontSize:11,color:C.amarillo,fontFace:"Arial",bold:true,margin:0
  });

  s1.addImage({ path:"D:/Proyectos/minenergia/sddp/outputs/aportes_enos.png", x:0.4,y:1.5,w:9.2,h:3.6 });

  s1.addShape(pres.shapes.RECTANGLE, { x:0.4,y:4.97,w:9.2,h:0.30, fill:{color:C.amarillo},line:{color:C.amarillo} });
  s1.addText("En los tres eventos El Niño, los aportes caen sistemáticamente hacia el umbral de alerta — justificando una política de reserva térmica anticipada.", {
    x:0.55,y:4.99,w:8.8,h:0.26, fontSize:10.5,bold:true,color:C.gris,fontFace:"Arial",margin:0
  });

  // ── SLIDE 2: Distribución Normal vs Niño ───
  let s2 = pres.addSlide();
  s2.background = { color: C.blanco };
  addHeader(s2, pres, "Impacto estadístico de El Niño en los aportes hídricos");
  addFooter(s2, pres, "D2");

  s2.addShape(pres.shapes.RECTANGLE, { x:0.4,y:0.95,w:9.2,h:0.46, fill:{color:C.gris},line:{color:C.gris} });
  s2.addText("4.655 días en condiciones normales vs 1.007 días en eventos El Niño — datos XM 2010-2026.", {
    x:0.55,y:0.97,w:8.8,h:0.42, fontSize:11,color:C.amarillo,fontFace:"Arial",bold:true,margin:0
  });

  s2.addImage({ path:"D:/Proyectos/minenergia/sddp/outputs/distribucion_nino_vs_normal.png", x:0.4,y:1.5,w:9.2,h:3.3 });

  // 3 tarjetas de números clave
  const stats = [
    { label:"Promedio normal", valor:"1.02", color:C.azulMd },
    { label:"Promedio El Niño", valor:"0.82", color:C.naranja },
    { label:"Reducción", valor:"−20%", color:"A00000" },
  ];
  stats.forEach((st, i) => {
    const x = 0.4 + i * 3.1;
    s2.addShape(pres.shapes.RECTANGLE, {
      x, y:4.88, w:2.95, h:0.42,
      fill:{color:st.color}, line:{color:st.color}
    });
    s2.addText(`${st.label}: ${st.valor}`, {
      x:x+0.1, y:4.90, w:2.75, h:0.38,
      fontSize:12, bold:true, color:C.blanco, fontFace:"Arial", align:"center", margin:0
    });
  });

  // ── SLIDE 3: Monte Carlo trayectorias ───────
  let s3 = pres.addSlide();
  s3.background = { color: C.blanco };
  addHeader(s3, pres, "Simulación Monte Carlo — 1.000 trayectorias Jul–Dic 2026");
  addFooter(s3, pres, "D3");

  s3.addShape(pres.shapes.RECTANGLE, { x:0.4,y:0.95,w:9.2,h:0.46, fill:{color:C.gris},line:{color:C.gris} });
  s3.addText("En escenario El Niño, el rango 25-75% de trayectorias se acerca al umbral de alerta desde julio. En escenario normal el sistema opera con margen.", {
    x:0.55,y:0.97,w:8.8,h:0.42, fontSize:11,color:C.amarillo,fontFace:"Arial",bold:true,margin:0
  });

  s3.addImage({ path:"D:/Proyectos/minenergia/sddp/outputs/montecarlo_trayectorias.png", x:0.4,y:1.5,w:9.2,h:3.3 });

  const mc_stats = [
    { label:"Escenarios simulados", valor:"1.000", color:C.azulMd },
    { label:"Horizonte", valor:"6 meses", color:C.verde },
    { label:"Fase actual", valor:"Moderado", color:C.naranja },
  ];
  mc_stats.forEach((st, i) => {
    const x = 0.4 + i * 3.1;
    s3.addShape(pres.shapes.RECTANGLE, {
      x, y:4.88, w:2.95, h:0.42,
      fill:{color:st.color}, line:{color:st.color}
    });
    s3.addText(`${st.label}: ${st.valor}`, {
      x:x+0.1, y:4.90, w:2.75, h:0.38,
      fontSize:12, bold:true, color:C.blanco, fontFace:"Arial", align:"center", margin:0
    });
  });

  // ── SLIDE 4: CVaR + estado actual ──────────
  let s4 = pres.addSlide();
  s4.background = { color: C.blanco };
  addHeader(s4, pres, "Análisis CVaR y estado actual del sistema — junio 2026");
  addFooter(s4, pres, "D4");

  s4.addShape(pres.shapes.RECTANGLE, { x:0.4,y:0.95,w:9.2,h:0.46, fill:{color:C.gris},line:{color:C.gris} });
  s4.addText("Hoy: aportes en 0.87 — por debajo del promedio normal (1.02) y cerca del promedio El Niño (0.82). Probabilidad de crisis: 14.7% normal / 26.8% El Niño.", {
    x:0.55,y:0.97,w:8.8,h:0.42, fontSize:11,color:C.amarillo,fontFace:"Arial",bold:true,margin:0
  });

  // Imagen estado actual arriba
  s4.addImage({ path:"D:/Proyectos/minenergia/sddp/outputs/estado_actual_aportes.png", x:0.4,y:1.5,w:9.2,h:1.9 });

  // Imagen CVaR abajo
  s4.addImage({ path:"D:/Proyectos/minenergia/sddp/outputs/riesgo_cvar.png", x:0.4,y:3.45,w:9.2,h:1.5 });

  s4.addShape(pres.shapes.RECTANGLE, { x:0.4,y:4.97,w:9.2,h:0.30, fill:{color:C.amarillo},line:{color:C.amarillo} });
  s4.addText("El sistema opera hoy en zona moderada — a 0.05 puntos del promedio El Niño. Este modelo permite cuantificar el costo de ese riesgo.", {
    x:0.55,y:4.99,w:8.8,h:0.26, fontSize:10.5,bold:true,color:C.gris,fontFace:"Arial",margin:0
  });

  await pres.writeFile({ fileName:"D:/Proyectos/minenergia/sddp/outputs/MinEnergia_Avance_Datos.pptx" });
  console.log("OK — guardado en outputs/MinEnergia_Avance_Datos.pptx");
}
build().catch(e => { console.error(e); process.exit(1); });
