#!/usr/bin/env node
/**
 * Present cut of the working offer.
 * Same facts as ways-to-work.html. Landscape, one idea per slide.
 * Do not edit the PPTX. Change this file (or the HTML), then rebuild.
 */

const pptxgen = require("pptxgenjs");

const W = 13.333;
const H = 7.5;
const M = 0.62;

const NIGHT = "1A1A2E";
const PURPLE = "7C3AED";
const PURPLE_LIGHT = "F3F0FF";
const STONE = "4A4A68";
const BODY = "2D2D3F";
const MUTED = "71717A";
const BORDER = "E4E4E7";
const BG = "FAFAFA";
const WHITE = "FFFFFF";

const SERIF = "Georgia";
const SANS = "Calibri";

const TOTAL = 11;

function pres() {
  const p = new pptxgen();
  p.defineLayout({ name: "RUA_16x9", width: W, height: H });
  p.layout = "RUA_16x9";
  p.author = "Rua Social";
  p.title = "How we work together";
  p.subject = "Working offer, August 2026";
  return p;
}

function label(slide, text, x, y, w, color) {
  slide.addText(text, {
    x, y, w, h: 0.28,
    fontFace: SANS, fontSize: 11, bold: true,
    color, charSpacing: 2.4, margin: 0,
  });
}

function footer(slide, n, onDark) {
  const color = onDark ? "8A8A9A" : MUTED;
  slide.addText("Rua Social  ·  Working offer, August 2026", {
    x: M, y: H - 0.42, w: 7.5, h: 0.24,
    fontFace: SANS, fontSize: 11, color, margin: 0,
  });
  slide.addText(`${String(n).padStart(2, "0")}  /  ${String(TOTAL).padStart(2, "0")}`, {
    x: W - M - 1.6, y: H - 0.42, w: 1.6, h: 0.24,
    fontFace: SANS, fontSize: 11, color, align: "right", margin: 0,
  });
}

function build() {
  const p = pres();

  // 1. Cover
  {
    const s = p.addSlide();
    s.background = { color: NIGHT };
    s.addText("RUA SOCIAL", {
      x: M, y: 0.55, w: 6, h: 0.28,
      fontFace: SANS, fontSize: 12, bold: true,
      color: "8A8A9A", charSpacing: 3.2, margin: 0,
    });
    label(s, "WORKING OFFER", M, 2.15, 6, PURPLE);
    s.addText("How we work together.", {
      x: M, y: 2.5, w: 11.2, h: 1.35,
      fontFace: SERIF, fontSize: 48, italic: true,
      color: WHITE, margin: 0,
    });
    s.addShape(p.shapes.RECTANGLE, {
      x: M, y: 3.95, w: 0.85, h: 0.07, fill: { color: PURPLE }, line: { color: PURPLE },
    });
    s.addText("You bring the business need and the last yes. Rua plans, shoots, and delivers a defined body of work with a clear finish.", {
      x: M, y: 4.25, w: 9.2, h: 0.85,
      fontFace: SANS, fontSize: 18, color: "B8B8C4", margin: 0,
    });
    s.addText("August 2026     Euro, exclusive of VAT     Three retainers, plus a project", {
      x: M, y: H - 0.42, w: 11.5, h: 0.24,
      fontFace: SANS, fontSize: 12, color: "8A8A9A", margin: 0,
    });
  }

  // 2. The deal
  {
    const s = p.addSlide();
    s.background = { color: NIGHT };
    label(s, "THE DEAL", M, M, 6, PURPLE);
    s.addText("You bring the business need\nand the last yes.", {
      x: M, y: 1.7, w: 12, h: 2.4,
      fontFace: SERIF, fontSize: 40, italic: true, color: WHITE, margin: 0,
    });
    s.addText("Rua plans, shoots, and delivers a defined body of work with a clear finish.", {
      x: M, y: 4.5, w: 10, h: 0.7,
      fontFace: SANS, fontSize: 20, color: "B8B8C4", margin: 0,
    });
    footer(s, 2, true);
  }

  // 3. Map of the offer
  {
    const s = p.addSlide();
    s.background = { color: BG };
    label(s, "THE INVESTMENT", M, 0.38, 6, PURPLE);
    s.addText("Three retainers, or a project.", {
      x: M, y: 0.7, w: 11, h: 0.55,
      fontFace: SERIF, fontSize: 28, italic: true, color: NIGHT, margin: 0,
    });
    s.addText("Monthly work is paid in advance. A project is 50 percent to confirm and 50 percent on delivery. Dates are held only when that first payment lands.", {
      x: M, y: 1.28, w: 12, h: 0.42,
      fontFace: SANS, fontSize: 14, color: STONE, margin: 0,
    });

    const cards = [
      { kicker: "RETAINER 01", name: "Edit", price: "€1,200", note: "Footage you already have", rec: false },
      { kicker: "RETAINER 02  ·  RECOMMENDED", name: "Monthly", price: "€2,500", note: "One shoot, then the month", rec: true },
      { kicker: "RETAINER 03", name: "Studio", price: "€4,000", note: "Two days, higher volume", rec: false },
    ];
    const gap = 0.22;
    const cw = (W - M * 2 - gap * 2) / 3;
    cards.forEach((c, i) => {
      const x = M + i * (cw + gap);
      const y = 1.95;
      s.addShape(p.shapes.ROUNDED_RECTANGLE, {
        x, y, w: cw, h: 3.35,
        fill: { color: c.rec ? NIGHT : WHITE },
        line: { color: c.rec ? NIGHT : BORDER, width: 1 },
        rectRadius: 0.1,
      });
      s.addText(c.kicker, {
        x: x + 0.28, y: y + 0.28, w: cw - 0.56, h: 0.28,
        fontFace: SANS, fontSize: 11, bold: true,
        color: c.rec ? "C4B5FD" : MUTED, charSpacing: 1.4, margin: 0,
      });
      s.addText(c.name, {
        x: x + 0.28, y: y + 0.7, w: cw - 0.56, h: 0.55,
        fontFace: SERIF, fontSize: 28, italic: true,
        color: c.rec ? WHITE : NIGHT, margin: 0,
      });
      s.addText(c.price, {
        x: x + 0.28, y: y + 1.35, w: cw - 0.56, h: 0.55,
        fontFace: SERIF, fontSize: 32, italic: true, color: PURPLE, margin: 0,
      });
      s.addText("per month, ex VAT", {
        x: x + 0.28, y: y + 1.92, w: cw - 0.56, h: 0.28,
        fontFace: SANS, fontSize: 13, color: c.rec ? "B8B8C4" : MUTED, margin: 0,
      });
      s.addText(c.note, {
        x: x + 0.28, y: y + 2.45, w: cw - 0.56, h: 0.55,
        fontFace: SANS, fontSize: 15, color: c.rec ? "D6D6DE" : STONE, margin: 0,
      });
    });
    s.addText("A project sits beside these. From €2,500, 50 / 50, no monthly obligation.", {
      x: M, y: 5.5, w: 12, h: 0.32,
      fontFace: SANS, fontSize: 14, color: STONE, margin: 0,
    });
    footer(s, 3, false);
  }

  function retainerSlide(opts) {
    const s = p.addSlide();
    s.background = { color: opts.dark ? NIGHT : WHITE };
    const leftY = 1.55;
    label(s, opts.kicker, M, leftY, 6.2, opts.dark ? "C4B5FD" : PURPLE);
    s.addText(opts.name, {
      x: M, y: leftY + 0.38, w: 5.8, h: 0.72,
      fontFace: SERIF, fontSize: 44, italic: true,
      color: opts.dark ? WHITE : NIGHT, margin: 0,
    });
    s.addText(opts.price, {
      x: M, y: leftY + 1.15, w: 5.8, h: 0.68,
      fontFace: SERIF, fontSize: 40, italic: true, color: PURPLE, margin: 0,
    });
    s.addText("per month, ex VAT", {
      x: M, y: leftY + 1.85, w: 5.8, h: 0.3,
      fontFace: SANS, fontSize: 16,
      color: opts.dark ? "B8B8C4" : MUTED, margin: 0,
    });
    s.addText(opts.blurb, {
      x: M, y: leftY + 2.4, w: 5.6, h: 1.2,
      fontFace: SANS, fontSize: 18,
      color: opts.dark ? "D6D6DE" : STONE, margin: 0,
    });
    opts.items.forEach((t, i) => {
      const y = 1.2 + i * 1.12;
      s.addShape(p.shapes.ROUNDED_RECTANGLE, {
        x: 7.15, y, w: 5.55, h: 0.98,
        fill: { color: opts.dark ? "12121F" : BG },
        line: { color: opts.dark ? "2A2A40" : BORDER, width: 1 },
        rectRadius: 0.08,
      });
      s.addText(t, {
        x: 7.4, y: y + 0.26, w: 5.1, h: 0.46,
        fontFace: SANS, fontSize: 16,
        color: opts.dark ? WHITE : BODY, margin: 0, valign: "middle",
      });
    });
    footer(s, opts.n, !!opts.dark);
  }

  retainerSlide({
    n: 4, kicker: "RETAINER 01", name: "Edit", price: "€1,200",
    blurb: "You already have the footage. We turn it into finished pieces, ready to post.",
    items: [
      "Up to 8 edited pieces a month",
      "Captions, titles, platform formats",
      "One revision round per piece",
      "No shoot day",
    ],
  });

  retainerSlide({
    n: 5, dark: true, kicker: "RETAINER 02  ·  RECOMMENDED", name: "Monthly", price: "€2,500",
    blurb: "One shoot day and the month's output. The usual way to stay in a rhythm.",
    items: [
      "One full shoot day",
      "10 or more finished pieces",
      "Planning call, captions, titles",
      "One revision round",
    ],
  });

  retainerSlide({
    n: 6, kicker: "RETAINER 03", name: "Studio", price: "€4,000",
    blurb: "Higher volume. Two shoot days, more finished work, a monthly review.",
    items: [
      "Two shoot days",
      "20 or more finished pieces",
      "Monthly review of what ran",
      "One revision round",
    ],
  });

  // 7. Project
  {
    const s = p.addSlide();
    s.background = { color: WHITE };
    label(s, "AD HOC", M, 0.45, 5, PURPLE);
    s.addText("A project.", {
      x: M, y: 0.9, w: 7, h: 0.8,
      fontFace: SERIF, fontSize: 44, italic: true, color: NIGHT, margin: 0,
    });
    s.addShape(p.shapes.ROUNDED_RECTANGLE, {
      x: 8.35, y: 0.85, w: 4.35, h: 1.55,
      fill: { color: PURPLE_LIGHT }, line: { color: PURPLE_LIGHT }, rectRadius: 0.1,
    });
    s.addText("From €2,500", {
      x: 8.55, y: 1.0, w: 4.0, h: 0.7,
      fontFace: SERIF, fontSize: 32, italic: true, color: PURPLE, margin: 0,
    });
    s.addText("ex VAT  ·  50 / 50", {
      x: 8.55, y: 1.7, w: 4.0, h: 0.35,
      fontFace: SANS, fontSize: 16, color: STONE, margin: 0,
    });
    s.addText("A defined sprint with a finish: research, concepts, one shoot day, a bank of 10 or more pieces. No monthly obligation.", {
      x: M, y: 2.5, w: 12, h: 1.1,
      fontFace: SANS, fontSize: 22, color: BODY, margin: 0,
    });
    s.addText("If the sprint works, a retainer conversation is then worth both sides' time.", {
      x: M, y: 3.7, w: 12, h: 0.55,
      fontFace: SERIF, fontSize: 22, italic: true, color: NIGHT, margin: 0,
    });
    const chips = ["Research", "Concepts", "One shoot day", "10 or more pieces"];
    const chipW = 2.85;
    chips.forEach((c, i) => {
      const x = M + i * (chipW + 0.18);
      s.addShape(p.shapes.ROUNDED_RECTANGLE, {
        x, y: 4.55, w: chipW, h: 0.7,
        fill: { color: BG }, line: { color: BORDER, width: 1 }, rectRadius: 0.08,
      });
      s.addText(c, {
        x, y: 4.55, w: chipW, h: 0.7,
        fontFace: SANS, fontSize: 15, color: NIGHT,
        align: "center", valign: "middle", margin: 0,
      });
    });
    footer(s, 7, false);
  }

  // 8. How it starts
  {
    const s = p.addSlide();
    s.background = { color: BG };
    label(s, "HOW IT STARTS", M, 0.38, 6, PURPLE);
    s.addText("Pick a shape. Then we write it down.", {
      x: M, y: 0.7, w: 12, h: 0.55,
      fontFace: SERIF, fontSize: 26, italic: true, color: NIGHT, margin: 0,
    });
    const steps = [
      { n: "1", t: "Choose a retainer, or a project.", d: "If you are unsure, say what you need done and by when. I will recommend one shape." },
      { n: "2", t: "We fill a short scope of work.", d: "Deliverables, floor, inclusions, exclusions, the decision owner, and the price. Email is enough to agree it." },
      { n: "3", t: "First payment confirms the work.", d: "Retainers: the first month in advance. A project: 50 percent. Dates are held only once that lands." },
    ];
    const gap = 0.22;
    const cw = (W - M * 2 - gap * 2) / 3;
    steps.forEach((st, i) => {
      const x = M + i * (cw + gap);
      s.addShape(p.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.55, w: cw, h: 4.55,
        fill: { color: WHITE }, line: { color: BORDER, width: 1 }, rectRadius: 0.1,
      });
      s.addShape(p.shapes.OVAL, {
        x: x + 0.3, y: 1.85, w: 0.55, h: 0.55,
        fill: { color: PURPLE }, line: { color: PURPLE },
      });
      s.addText(st.n, {
        x: x + 0.3, y: 1.85, w: 0.55, h: 0.55,
        fontFace: SANS, fontSize: 16, bold: true, color: WHITE,
        align: "center", valign: "middle", margin: 0,
      });
      s.addText(st.t, {
        x: x + 0.3, y: 2.6, w: cw - 0.6, h: 1.15,
        fontFace: SERIF, fontSize: 20, italic: true, color: NIGHT, margin: 0,
      });
      s.addText(st.d, {
        x: x + 0.3, y: 3.9, w: cw - 0.6, h: 1.7,
        fontFace: SANS, fontSize: 15, color: STONE, margin: 0,
      });
    });
    footer(s, 8, false);
  }

  // 9. The floor
  {
    const s = p.addSlide();
    s.background = { color: WHITE };
    label(s, "THE FLOOR", M, 1.5, 6, PURPLE);
    s.addText("Each option names a conservative quantity.", {
      x: M, y: 2.0, w: 12, h: 1.0,
      fontFace: SERIF, fontSize: 32, italic: true, color: NIGHT, margin: 0,
    });
    s.addText("Extra output, when it happens, is one-off. It does not raise the next month's obligation or change the price on its own.", {
      x: M, y: 3.2, w: 11, h: 1.1,
      fontFace: SANS, fontSize: 20, color: STONE, margin: 0,
    });
    footer(s, 9, false);
  }

  // 10. Included / not
  {
    const s = p.addSlide();
    s.background = { color: BG };
    label(s, "THE TERMS", M, 0.38, 6, PURPLE);
    s.addText("What sits in the price, and what does not.", {
      x: M, y: 0.7, w: 12, h: 0.5,
      fontFace: SERIF, fontSize: 26, italic: true, color: NIGHT, margin: 0,
    });
    const colW = (W - M * 2 - 0.28) / 2;
    const left = [
      "Planning, kit, edit and grade for the committed work",
      "Captions, on-screen titles, platform formats",
      "One revision round per piece, 48-hour feedback windows",
      "Usage on your own site and social channels",
    ];
    const right = [
      "Ongoing posting or channel management",
      "Paid media, boosting, or ads",
      "Extra shoot days, or usage beyond your own channels",
      "Strategy beyond the agreed engagement",
    ];
    function column(title, items, x, dark) {
      s.addShape(p.shapes.RECTANGLE, {
        x, y: 1.45, w: colW, h: 5.05,
        fill: { color: WHITE }, line: { color: BORDER, width: 1 },
      });
      s.addText(title, {
        x: x + 0.35, y: 1.68, w: colW - 0.7, h: 0.4,
        fontFace: SANS, fontSize: 14, bold: true,
        color: dark ? NIGHT : PURPLE, charSpacing: 1.4, margin: 0,
      });
      items.forEach((t, i) => {
        s.addText(t, {
          x: x + 0.35, y: 2.25 + i * 0.95, w: colW - 0.7, h: 0.75,
          fontFace: SANS, fontSize: 16, color: BODY, margin: 0,
        });
      });
    }
    column("INCLUDED", left, M, false);
    column("NOT INCLUDED", right, M + colW + 0.28, true);
    footer(s, 10, false);
  }

  // 11. Close
  {
    const s = p.addSlide();
    s.background = { color: NIGHT };
    label(s, "NEXT", M, 1.35, 5, PURPLE);
    s.addText("Pick a shape.\nThen we write it down.", {
      x: M, y: 1.75, w: 12, h: 1.8,
      fontFace: SERIF, fontSize: 36, italic: true, color: WHITE, margin: 0,
    });
    s.addText("Nothing here is a confirmed engagement. The scope of work is the contract. The first payment is the gate.", {
      x: M, y: 3.75, w: 10.5, h: 0.75,
      fontFace: SANS, fontSize: 18, color: "B8B8C4", margin: 0,
    });
    s.addText("Darragh Hoare     darragh@ruasocial.ie     +353 85 715 0077", {
      x: M, y: H - 0.42, w: 12, h: 0.24,
      fontFace: SANS, fontSize: 14, color: "B8B8C4", margin: 0,
    });
  }

  const out = `${__dirname}/ways-to-work-present.pptx`;
  return p.writeFile({ fileName: out }).then(() => out);
}

build()
  .then((out) => console.log("wrote", out))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
