/**
 * Resume Template Generator (Node.js / docx)
 * Section order: Experience → Projects → Skills → Certifications → Education
 * 2-page layout with 10pt body text and breathing room
 */

const fs = require("fs");
const {
  Document,
  Paragraph,
  TextRun,
  HeadingLevel,
  AlignmentType,
  Packer,
  ExternalHyperlink,
  TabStopType,
  TabStopPosition,
  PageBreak,
} = require("docx");

const FONT = "Calibri";
const FONT_SIZE_NAME = 32;       // 16pt
const FONT_SIZE_CONTACT = 20;   // 10pt
const FONT_SIZE_HEADING = 24;   // 12pt
const FONT_SIZE_BODY = 20;      // 10pt

const PRIORITY_BOLD = [
  "Azure Blob Storage", "Azure", "Power BI", "Power Query", "Power Automate",
  "Python", "SQL", "DAX", "MySQL", "ETL",
  "FLAIR", "FOCUS", "HMGP", "FEMA", "ARIMA", "Prophet",
  "Flask", "MongoDB", "Selenium", "Scikit-learn", "LangChain",
  "Snowflake", "PostgreSQL", "SQL Server", "Spark", "Airflow",
  "Databricks", "GCP", "AWS", "Docker", "REST API", "FastAPI",
];

const NEVER_BOLD = new Set([
  "SHA-256", "KPIs", "SLA", "CSRF", ".NET", "VBA", "Git", "GitHub",
  "SharePoint", "OneDrive", "Windows Task Scheduler", "Excel", "JSON", "CSV", "XML",
]);

const SKIP_LEADERSHIP_STARTS = [
  "Collaborated", "Onboarded", "Trained", "Presented", "Authored",
  "Led a", "Worked with", "Partnered",
];

function splitBulletWithBolds(text, matchedKeywords, maxBolds = 2) {
  if (!text) return [new TextRun({ text: "", font: FONT, size: FONT_SIZE_BODY })];

  const textTrimmed = text.trim();
  for (const prefix of SKIP_LEADERSHIP_STARTS) {
    if (textTrimmed.startsWith(prefix)) {
      return [new TextRun({ text, font: FONT, size: FONT_SIZE_BODY })];
    }
  }

  const termsToCheck = PRIORITY_BOLD.filter(
    t => !NEVER_BOLD.has(t) &&
      (!matchedKeywords || matchedKeywords.length === 0 ||
        matchedKeywords.some(kw =>
          kw.toLowerCase().includes(t.toLowerCase()) ||
          t.toLowerCase().includes(kw.toLowerCase())
        ))
  );
  const sortedTerms = termsToCheck.sort((a, b) => b.length - a.length);

  const midpoint = Math.floor(text.length / 2);
  let segments = [{ text, bold: false, startOffset: 0 }];
  let boldCount = 0;

  for (const term of sortedTerms) {
    if (boldCount >= maxBolds) break;
    const newSegments = [];
    let didBold = false;
    for (const seg of segments) {
      if (seg.bold || didBold) { newSegments.push({ ...seg }); continue; }
      const idx = seg.text.toLowerCase().indexOf(term.toLowerCase());
      if (idx === -1) { newSegments.push({ ...seg }); continue; }
      const globalIdx = (seg.startOffset !== undefined ? seg.startOffset : 0) + idx;
      if (globalIdx >= midpoint) { newSegments.push({ ...seg }); continue; }
      const before = seg.text.slice(0, idx);
      const match = seg.text.slice(idx, idx + term.length);
      const after = seg.text.slice(idx + term.length);
      const so = seg.startOffset !== undefined ? seg.startOffset : 0;
      if (before) newSegments.push({ text: before, bold: false, startOffset: so });
      newSegments.push({ text: match, bold: true, startOffset: so + idx });
      if (after) newSegments.push({ text: after, bold: false, startOffset: so + idx + term.length });
      didBold = true;
      boldCount++;
    }
    if (didBold) segments = newSegments;
  }

  return segments.map(seg =>
    new TextRun({
      text: seg.text,
      bold: seg.bold || false,
      font: FONT,
      size: FONT_SIZE_BODY,
    })
  );
}

function formatDate(dateStr) {
  if (!dateStr) return "Present";
  const months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];
  const parts = dateStr.split("-");
  if (parts.length >= 2) {
    const year = parts[0];
    const monthIdx = parseInt(parts[1], 10) - 1;
    if (monthIdx >= 0 && monthIdx < 12) {
      return `${months[monthIdx]} ${year}`;
    }
  }
  return dateStr;
}

function buildHeader(personal) {
  const children = [];

  children.push(
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 60 },
      children: [
        new TextRun({ text: personal.name || "", bold: true, size: FONT_SIZE_NAME, font: FONT }),
      ],
    })
  );

  const contactParts = [];
  if (personal.location) contactParts.push(personal.location);
  if (personal.phone) contactParts.push(personal.phone);
  if (personal.email) contactParts.push(personal.email);

  if (contactParts.length > 0) {
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 40 },
        children: [
          new TextRun({ text: contactParts.join(" | "), size: FONT_SIZE_CONTACT, font: FONT }),
        ],
      })
    );
  }

  const linkParts = [];
  if (personal.linkedin) {
    const linkedinUrl = personal.linkedin.startsWith("http")
      ? personal.linkedin
      : `https://${personal.linkedin}`;
    linkParts.push(
      new ExternalHyperlink({
        link: linkedinUrl,
        children: [
          new TextRun({ text: personal.linkedin, size: FONT_SIZE_CONTACT, font: FONT, color: "0000FF" }),
        ],
      })
    );
  }
  if (personal.github) {
    const githubUrl = personal.github.startsWith("http")
      ? personal.github
      : `https://${personal.github}`;
    if (linkParts.length > 0) {
      linkParts.push(new TextRun({ text: " | ", size: FONT_SIZE_CONTACT, font: FONT }));
    }
    linkParts.push(
      new ExternalHyperlink({
        link: githubUrl,
        children: [
          new TextRun({ text: personal.github, size: FONT_SIZE_CONTACT, font: FONT, color: "0000FF" }),
        ],
      })
    );
  }
  if (personal.portfolio) {
    const portfolioUrl = personal.portfolio.startsWith("http")
      ? personal.portfolio
      : `https://${personal.portfolio}`;
    if (linkParts.length > 0) {
      linkParts.push(new TextRun({ text: " | ", size: FONT_SIZE_CONTACT, font: FONT }));
    }
    linkParts.push(
      new ExternalHyperlink({
        link: portfolioUrl,
        children: [
          new TextRun({ text: personal.portfolio, size: FONT_SIZE_CONTACT, font: FONT, color: "0000FF" }),
        ],
      })
    );
  }

  if (linkParts.length > 0) {
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 120 },
        children: linkParts,
      })
    );
  }

  return children;
}

function sectionHeading(title) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 160, after: 60 },
    border: { bottom: { color: "000000", size: 6, space: 1, style: "single" } },
    children: [
      new TextRun({ text: title.toUpperCase(), bold: true, size: FONT_SIZE_HEADING, font: FONT }),
    ],
  });
}

function buildExperience(jobs) {
  const children = [sectionHeading("Professional Experience")];

  for (const job of jobs) {
    const startFormatted = formatDate(job.start_date);
    const endFormatted = formatDate(job.end_date);
    const dateRange = `${startFormatted} – ${endFormatted}`;
    
    // Format: "Company, Title | Date Range"
    children.push(
      new Paragraph({
        spacing: { before: 120, after: 40 },
        children: [
          new TextRun({ text: `${job.company}, `, bold: true, size: FONT_SIZE_BODY, font: FONT }),
          new TextRun({ text: job.title, bold: true, size: FONT_SIZE_BODY, font: FONT }),
          new TextRun({ text: ` | ${dateRange}`, size: FONT_SIZE_BODY, font: FONT }),
        ],
      })
    );

    if (job.location) {
      children.push(
        new Paragraph({
          spacing: { after: 40 },
          children: [
            new TextRun({ text: job.location, italics: true, size: FONT_SIZE_BODY, font: FONT }),
          ],
        })
      );
    }

    for (const bullet of job.bullets || []) {
      const text = typeof bullet === "string" ? bullet : bullet.text || "";
      const matchedKeywords = (typeof bullet === "object" && bullet) ? (bullet.matched_keywords || []) : [];
      if (text) {
        children.push(
          new Paragraph({
            bullet: { level: 0 },
            spacing: { after: 40 },
            children: splitBulletWithBolds(text, matchedKeywords),
          })
        );
      }
    }
  }

  return children;
}

function buildProjects(projects, isCv = false) {
  if (!projects || projects.length === 0) return [];

  const children = [sectionHeading("Projects")];

  // CV: all projects; Resume: top 3
  const topProjects = isCv ? projects : projects.slice(0, 3);
  
  for (const proj of topProjects) {
    const titleParts = [
      new TextRun({ text: proj.name, bold: true, size: FONT_SIZE_BODY, font: FONT }),
    ];

    if (proj.github_url && proj.github_url.startsWith("http")) {
      titleParts.push(new TextRun({ text: " — ", size: FONT_SIZE_BODY, font: FONT }));
      titleParts.push(
        new ExternalHyperlink({
          link: proj.github_url,
          children: [
            new TextRun({ text: "GitHub", size: FONT_SIZE_BODY, font: FONT, color: "0000FF" }),
          ],
        })
      );
    }

    children.push(
      new Paragraph({
        spacing: { before: 120, after: 40 },
        children: titleParts,
      })
    );

    for (const bullet of proj.bullets || []) {
      const text = typeof bullet === "string" ? bullet : bullet.text || "";
      const matchedKeywords = (typeof bullet === "object" && bullet) ? (bullet.matched_keywords || []) : [];
      if (text) {
        children.push(
          new Paragraph({
            bullet: { level: 0 },
            spacing: { after: 40 },
            children: splitBulletWithBolds(text, matchedKeywords),
          })
        );
      }
    }
  }

  return children;
}

function buildSkills(skills) {
  if (!skills || skills.length === 0) return [];

  const children = [sectionHeading("Technical Skills")];

  const byCategory = {};
  for (const skill of skills) {
    const cat = skill.category || "Other";
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(skill.name);
  }

  for (const [category, names] of Object.entries(byCategory)) {
    children.push(
      new Paragraph({
        spacing: { before: 40, after: 40 },
        children: [
          new TextRun({ text: `${category}: `, bold: true, size: FONT_SIZE_BODY, font: FONT }),
          new TextRun({ text: names.join(", "), size: FONT_SIZE_BODY, font: FONT }),
        ],
      })
    );
  }

  return children;
}

function buildCertifications(certifications) {
  if (!certifications || certifications.length === 0) return [];

  const children = [sectionHeading("Certifications")];

  for (const cert of certifications) {
    const parts = [cert.name];
    if (cert.issuer) parts.push(cert.issuer);
    if (cert.issued) parts.push(formatDate(cert.issued));

    children.push(
      new Paragraph({
        bullet: { level: 0 },
        spacing: { after: 40 },
        children: [
          new TextRun({ text: parts.join(" — "), size: FONT_SIZE_BODY, font: FONT }),
        ],
      })
    );
  }

  return children;
}

function buildEducation(education) {
  if (!education || education.length === 0) return [];

  const children = [sectionHeading("Education")];

  for (const edu of education) {
    const degreeLine = edu.field
      ? `${edu.degree} in ${edu.field}`
      : edu.degree;

    const rightPart = [];
    if (edu.end_date) rightPart.push(formatDate(edu.end_date));
    if (edu.gpa) rightPart.push(`GPA: ${edu.gpa}`);

    children.push(
      new Paragraph({
        spacing: { before: 80, after: 20 },
        children: [
          new TextRun({ text: degreeLine, bold: true, size: FONT_SIZE_BODY, font: FONT }),
          new TextRun({ text: rightPart.length ? ` | ${rightPart.join(" | ")}` : "", size: FONT_SIZE_BODY, font: FONT }),
        ],
      })
    );

    const institutionParts = [edu.institution];
    if (edu.location) institutionParts.push(edu.location);

    children.push(
      new Paragraph({
        spacing: { after: 40 },
        children: [
          new TextRun({ text: institutionParts.join(", "), italics: true, size: FONT_SIZE_BODY, font: FONT }),
        ],
      })
    );
  }

  return children;
}

function buildSummary(summary) {
  if (!summary) return [];
  return [
    sectionHeading("Professional Summary"),
    new Paragraph({
      spacing: { before: 80, after: 120 },
      children: [
        new TextRun({ text: summary, size: FONT_SIZE_BODY, font: FONT }),
      ],
    }),
  ];
}

async function generateCoverLetter(data, outputPath) {
  const personal = data.personal || {};
  const content = (data.content || "").split(/\n\n+/);

  const children = [];

  // Header
  children.push(
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 60 },
      children: [
        new TextRun({ text: personal.name || "", bold: true, size: FONT_SIZE_NAME, font: FONT }),
      ],
    })
  );
  const contactParts = [personal.location, personal.phone, personal.email].filter(Boolean);
  if (contactParts.length > 0) {
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
        children: [
          new TextRun({ text: contactParts.join(" | "), size: FONT_SIZE_CONTACT, font: FONT }),
        ],
      })
    );
  }

  // Date
  if (data.date) {
    children.push(
      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: data.date, size: FONT_SIZE_BODY, font: FONT })],
      })
    );
  }

  // Body paragraphs
  for (const para of content) {
    const lines = para.split(/\n/);
    for (let i = 0; i < lines.length; i++) {
      children.push(
        new Paragraph({
          spacing: { after: 60 },
          children: [
            new TextRun({ text: lines[i], size: FONT_SIZE_BODY, font: FONT }),
          ],
        })
      );
    }
  }

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            margin: { top: 720, right: 720, bottom: 720, left: 720 },
          },
        },
        children,
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`Cover letter generated: ${outputPath}`);
}

async function generateResume(data, outputPath) {
  const sections = [];

  // Header
  sections.push(...buildHeader(data.personal || {}));

  // Section order: Experience → Projects → Skills → Certifications → Education
  sections.push(...buildExperience(data.experience || []));
  sections.push(...buildProjects(data.projects || [], false));
  sections.push(...buildSkills(data.skills || []));
  sections.push(...buildCertifications(data.certifications || []));
  sections.push(...buildEducation(data.education || []));

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            margin: { top: 720, right: 720, bottom: 720, left: 720 },  // 0.5 inch margins
          },
        },
        children: sections,
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`Resume generated: ${outputPath}`);
}

async function generateCV(data, outputPath) {
  const sections = [];

  // Header
  sections.push(...buildHeader(data.personal || {}));

  // Professional Summary
  if (data.summary) {
    sections.push(...buildSummary(data.summary));
  }

  // Section order: Experience → Projects → Skills → Certifications → Education
  sections.push(...buildExperience(data.experience || []));
  sections.push(...buildProjects(data.projects || [], true));
  sections.push(...buildSkills(data.skills || []));
  sections.push(...buildCertifications(data.certifications || []));
  sections.push(...buildEducation(data.education || []));

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            margin: { top: 720, right: 720, bottom: 720, left: 720 },
          },
        },
        children: sections,
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`CV generated: ${outputPath}`);
}

const args = process.argv.slice(2);
const typeFlag = args.indexOf("--type");
const docType = typeFlag !== -1 ? args[typeFlag + 1] : "resume";
const inputFile = typeFlag !== -1 ? args[typeFlag + 2] : args[0];
const outputFile = typeFlag !== -1 ? args[typeFlag + 3] : args[1];

if (!inputFile || !outputFile) {
  console.error("Usage: node resume_template.js [--type resume|coverletter|cv] <input.json> <output.docx>");
  process.exit(1);
}

const rawData = fs.readFileSync(inputFile, "utf-8");
const data = JSON.parse(rawData);

const run = () => {
  if (docType === "coverletter") {
    return generateCoverLetter(data, outputFile);
  }
  if (docType === "cv") {
    return generateCV(data, outputFile);
  }
  return generateResume(data, outputFile);
};

run().catch((err) => {
  console.error("Error generating document:", err);
  process.exit(1);
});
