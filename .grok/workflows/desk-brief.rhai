let meta = #{
    name: "desk-brief",
    description: "Sit-down scan of Rua: studio and clients on grok-4.5, tools and Papa Rua on grok-4.6, then one 4.6 brief.",
    when_to_use: "When sitting down at the desk, asking what is on, or wanting a multi-agent org brief.",
    phases: [
        #{ title: "Scan", detail: "one reader per room" },
        #{ title: "Brief", detail: "one synthesis" },
    ],
};

let room_schema = #{
    "type": "object",
    "required": ["room", "status", "facts", "open_items", "do_not_invent"],
    "properties": #{
        "room": #{ "type": "string" },
        "status": #{ "type": "string" },
        "facts": #{
            "type": "array",
            "maxItems": 8,
            "items": #{ "type": "string" },
        },
        "open_items": #{
            "type": "array",
            "maxItems": 6,
            "items": #{ "type": "string" },
        },
        "do_not_invent": #{
            "type": "array",
            "maxItems": 4,
            "items": #{ "type": "string" },
        },
    },
};

let brief_schema = #{
    "type": "object",
    "required": ["headline", "live", "waiting", "recommended_next", "class", "why", "parked"],
    "properties": #{
        "headline": #{ "type": "string" },
        "live": #{
            "type": "array",
            "maxItems": 6,
            "items": #{ "type": "string" },
        },
        "waiting": #{
            "type": "array",
            "maxItems": 6,
            "items": #{ "type": "string" },
        },
        "recommended_next": #{ "type": "string" },
        "class": #{ "type": "string" },
        "why": #{ "type": "string" },
        "parked": #{
            "type": "array",
            "maxItems": 6,
            "items": #{ "type": "string" },
        },
    },
};

fn as_text(x) {
    if x == () {
        ""
    } else if type_of(x) == "string" {
        x
    } else {
        json_encode(x)
    }
}

fn bullets(items) {
    if items == () || type_of(items) != "array" || items.len() == 0 {
        return "- (none)\n";
    }
    let out = "";
    for item in items {
        out += "- " + as_text(item) + "\n";
    }
    out
}

let studio_prompt = "";
studio_prompt += "Scan the Rua studio room for a sit-down brief. Read-only.\n";
studio_prompt += "Use read_file on these paths before answering. Do not answer from memory.\n";
studio_prompt += "- 20-studio/README.md\n";
studio_prompt += "- 20-studio/desk.md\n";
studio_prompt += "- 20-studio/sales/README.md\n";
studio_prompt += "- 20-studio/founder-context.md\n";
studio_prompt += "Do not read founder-context-provenance.md.\n";
studio_prompt += "Do not invent a CRM, rate card, or commercial model for pickup.\n";
studio_prompt += "Do not treat any unadopted operating-direction candidate as policy.\n";
studio_prompt += "Report only what those files actually say. Empty or unresolved is a valid finding.\n";
studio_prompt += "Return {room, status, facts, open_items, do_not_invent}. room must be studio.";

let clients_prompt = "";
clients_prompt += "Scan Rua client instance records for a sit-down brief. Read-only.\n";
clients_prompt += "Use list_dir on 10-clients, then read_file on 10-clients/README.md ";
clients_prompt += "and every 10-clients/*/README.md that exists. Do not answer from memory.\n";
clients_prompt += "An empty list, or only delivered/dormant records, is a valid finding.\n";
clients_prompt += "Do not reconstruct sealed artefacts. Do not lift one client into a template.\n";
clients_prompt += "Do not open the reference map unless a README tells you a path is missing.\n";
clients_prompt += "Return {room, status, facts, open_items, do_not_invent}. room must be clients.";

let tools_prompt = "";
tools_prompt += "Scan Rua software tools for a sit-down brief.\n";
tools_prompt += "Use list_dir and read_file on 30-tools/README.md and each 30-tools/*/README.md.\n";
tools_prompt += "Run only: git status --short -- 30-tools && git log -5 --oneline -- 30-tools\n";
tools_prompt += "Do not answer from memory. Do not propose a new tool.\n";
tools_prompt += "Do not install dependencies or run builds.\n";
tools_prompt += "Return {room, status, facts, open_items, do_not_invent}. room must be tools.";

let papa_prompt = "";
papa_prompt += "Scan Papa Rua for a sit-down brief. Read-only.\n";
papa_prompt += "Use list_dir on 40-papa-rua, then read_file on 40-papa-rua/README.md ";
papa_prompt += "and any other markdown that actually exists there. Do not answer from memory.\n";
papa_prompt += "A stub directory is a valid finding. Do not invent a release, content, or live plan.\n";
papa_prompt += "Return {room, status, facts, open_items, do_not_invent}. room must be papa.";

phase("Scan");
log("Scanning studio+clients on grok-4.5, tools+papa on grok-4.6");

let scans = parallel([
    #{
        prompt: studio_prompt,
        label: "scan:studio",
        capability_mode: "read-only",
        output_schema: room_schema,
        model: "grok-4.5",
    },
    #{
        prompt: clients_prompt,
        label: "scan:clients",
        capability_mode: "read-only",
        output_schema: room_schema,
        model: "grok-4.5",
    },
    #{
        prompt: tools_prompt,
        label: "scan:tools",
        capability_mode: "execute",
        output_schema: room_schema,
        model: "grok-4.6",
    },
    #{
        prompt: papa_prompt,
        label: "scan:papa",
        capability_mode: "read-only",
        output_schema: room_schema,
        model: "grok-4.6",
    },
]);

let studio_json = json_encode(if scans[0] != () && scans[0].success { scans[0].output } else { () });
let clients_json = json_encode(if scans[1] != () && scans[1].success { scans[1].output } else { () });
let tools_json = json_encode(if scans[2] != () && scans[2].success { scans[2].output } else { () });
let papa_json = json_encode(if scans[3] != () && scans[3].success { scans[3].output } else { () });

let usable = 0;
if scans[0] != () && scans[0].success { usable += 1; }
if scans[1] != () && scans[1].success { usable += 1; }
if scans[2] != () && scans[2].success { usable += 1; }
if scans[3] != () && scans[3].success { usable += 1; }
log(usable.to_string() + "/4 room scans returned a usable result");

if usable == 0 {
    complete(#{
        summary: "All four room scans failed. Open 20-studio/desk.md and scan by hand.",
        headline: "Desk brief failed",
        live: [],
        waiting: [],
        recommended_next: "Open 20-studio/desk.md and name the class of the actual job.",
        class: "founder / direction",
        why: "The parallel scan returned no usable room reports.",
        parked: [],
    });
}

phase("Brief");

let synth_prompt = "";
synth_prompt += "Synthesize a Rua sit-down brief from these room scans. ";
synth_prompt += "Use read_file on 20-studio/founder-context.md and 20-studio/desk.md ";
synth_prompt += "before writing the brief. Do not answer from the JSON alone.\n";
synth_prompt += "Studio scan JSON:\n" + studio_json + "\n";
synth_prompt += "Clients scan JSON:\n" + clients_json + "\n";
synth_prompt += "Tools scan JSON:\n" + tools_json + "\n";
synth_prompt += "Papa scan JSON:\n" + papa_json + "\n";
synth_prompt += "Rules:\n";
synth_prompt += "- Recommend exactly one next action. Name its class ";
synth_prompt += "(client job, sales, tool / software, founder / direction, Papa Rua, or other).\n";
synth_prompt += "- If there is no live paid engagement, say so. Do not invent a client or a campaign.\n";
synth_prompt += "- Do not recommend hiring, a CRM, new top-level directories, ";
synth_prompt += "or an agents/orchestration layer.\n";
synth_prompt += "- Do not promote music-video work into a service line. ";
synth_prompt += "Keep it visible only if the files already keep it visible.\n";
synth_prompt += "- Do not treat unadopted operating direction as policy.\n";
synth_prompt += "- Park extras. Do not turn the brief into a backlog.\n";
synth_prompt += "- class must be one short label. recommended_next is one sentence.\n";
synth_prompt += "Return {headline, live, waiting, recommended_next, class, why, parked}.";

let synth = agent(synth_prompt, #{
    label: "desk-brief",
    capability_mode: "read-only",
    output_schema: brief_schema,
    model: "grok-4.6",
});

if synth == () || !synth.success || synth.output == () {
    complete(#{
        summary: "Room scans ran, synthesis failed. Use the raw room JSON.",
        studio: studio_json,
        clients: clients_json,
        tools: tools_json,
        papa: papa_json,
    });
}

let brief = synth.output;
let report = "";
report += "# Desk brief\n\n";
report += as_text(brief.headline) + "\n\n";
report += "## Live\n" + bullets(brief.live) + "\n";
report += "## Waiting\n" + bullets(brief.waiting) + "\n";
report += "## Do this next\n";
report += as_text(brief.recommended_next) + "\n\n";
report += "Class: " + as_text(brief.class) + "\n\n";
report += as_text(brief.why) + "\n\n";
report += "## Parked\n" + bullets(brief.parked);

let report_path = write_scratch_file("desk-brief.md", report);
complete(#{
    path: report_path,
    report: report,
    headline: brief.headline,
    recommended_next: brief.recommended_next,
    class: brief.class,
});
