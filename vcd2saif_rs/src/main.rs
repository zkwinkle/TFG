/// Based on ECASLab implementation.
/// https://github.com/ECASLab/ALS-benchmark-circuits/blob/main/vcd2saif.py
use chrono::Local;
use regex::Regex;
use std::env;
use std::fs::File;
use std::io::{self, BufRead, Write};
use std::path::Path;

struct Var {
    name: String,
    alias: String,
    parent: String,
    level: usize,
    len: usize,
    bit_index: usize,
    multi_bit: bool,
    high: u64,
    low: u64,
    x: u64,
    ig: u64,
    last: char,
    toggle: u64,
}

fn timestamp() -> String {
    Local::now().format("%m-%d-%Y %H:%M:%S").to_string()
}

fn indent(lvl: usize) -> String {
    "  ".repeat(lvl)
}

fn read_lines<P>(filename: P) -> io::Lines<io::BufReader<File>>
where
    P: AsRef<Path>,
{
    let f = File::open(filename).unwrap();
    io::BufReader::new(f).lines()
}

// (TODO copied from python code)
// #TODO: check saif information
const SAIF_VERSION: &'static str = "2.0";
const DIRECTION: &'static str = "backward";
const VENDOR: &'static str = "AxPy Inc";
const PROGRAM_NAME: &'static str = "open_vcd2saif";
const VERSION: &'static str = "v0";
const DIVIDER: &'static str = "/";
const TIMESCALE: &'static str = "1 ps";

fn main() {
    // Example call
    // cargo run -- BK_16b ../AxLS/build/.vcd 4000.saif
    let args: Vec<_> = env::args().collect();
    let module = &args[1];
    let vcd = &args[2];
    let saif = &args[3];

    // TODO: Remove verbose flag or try to replicate the original use case or
    // something else?
    let _verbose = args.get(4).map_or(false, |v| v == "-v");

    let mut vars = Vec::new();
    let mut level = 0;
    let mut parent = String::new();

    let re_scope = Regex::new(r"^\s*\$scope\s+\S+\s+(\S+)").unwrap();
    let re_up = Regex::new(r"^\s*\$upscope").unwrap();
    let re_var = Regex::new(r"\$var").unwrap();
    let re_bits = Regex::new(r"\d+").unwrap();

    // pass1
    for line in read_lines(vcd) {
        let line = line.unwrap();
        if let Some(cap) = re_scope.captures(&line) {
            parent = cap[1].to_string();
            level += 1;
            continue;
        }
        if re_up.is_match(&line) {
            level -= 1;
            continue;
        }
        if re_var.is_match(&line) {
            let parts: Vec<_> = line.split_ascii_whitespace().collect();

            let var_len: usize = parts[2].parse().unwrap();
            let alias = parts[3];
            let name = parts[4];

            let bits: Vec<_> = re_bits
                .find_iter(parts[5])
                .map(|m| m.as_str().parse::<usize>().unwrap())
                .collect();
            let (n0, multi) = match bits.as_slice() {
                [_, lo] => (*lo, true),
                [x] => (*x, true),
                _ => (1, false),
            };

            if var_len == 1 {
                vars.push(Var {
                    name: name.into(),
                    alias: alias.into(),
                    parent: parent.clone(),
                    level,
                    len: 1,
                    bit_index: n0,
                    multi_bit: multi,
                    high: 0,
                    low: 0,
                    x: 0,
                    ig: 0,
                    last: '2',
                    toggle: 0,
                });
            } else {
                for i in 0..var_len {
                    vars.push(Var {
                        name: name.into(),
                        alias: alias.into(),
                        parent: parent.clone(),
                        level,
                        len: var_len,
                        bit_index: i,
                        multi_bit: multi,
                        high: 0,
                        low: 0,
                        x: 0,
                        ig: 0,
                        last: '2',
                        toggle: 0,
                    });
                }
            }
        }
    }

    // pass2
    let mut last_step = 0_u64;
    let mut time_step;
    let re_time = Regex::new(r"^#(\d+)").unwrap();

    for line in read_lines(vcd) {
        let line = line.unwrap();

        if line.starts_with('#') {
            time_step = re_time.captures(&line).unwrap()[1].parse().unwrap();
            let diff = time_step - last_step;
            for v in &mut vars {
                match v.last {
                    '1' => v.high += diff,
                    '0' => v.low += diff,
                    'x' => v.x += diff,
                    _ => {}
                }
            }
            last_step = time_step;
        } else if line.starts_with('b') && !line.starts_with("bx") {
            let mut parts = line.split_ascii_whitespace();
            let (bits, alias) = (parts.next().unwrap(), parts.next().unwrap());

            let raw = bits.trim_start_matches('b');

            if !raw.chars().all(|c| c == '0' || c == '1') {
                panic!("Invalid bitstring: {}", raw);
            }

            let width = vars.iter().find(|v| &v.alias == alias).unwrap().len;
            let word = format!("{:0>width$}", raw, width = width);
            let rev: Vec<char> = word.chars().rev().collect();
            for v in &mut vars {
                if v.alias == alias {
                    let new = rev[v.bit_index];
                    if v.last != '2' && v.last != new {
                        v.toggle += 1;
                    }
                    v.last = new;
                }
            }
        } else if line.starts_with(['0', '1', 'x']) {
            let bit_val = line.chars().next().unwrap();
            let alias = &line[1..];
            for v in &mut vars {
                if v.alias == alias && v.len == 1 {
                    if v.last != '2' && v.last != bit_val {
                        v.toggle += 1;
                    }
                    v.last = bit_val;
                }
            }
        }
    }
    let duration = last_step.saturating_sub(1);

    // pass3

    let mut out = File::create(saif).unwrap();
    writeln!(out, "(SAIFILE").unwrap();
    writeln!(out, "(SAIFVERSION \"{SAIF_VERSION}\")").unwrap();
    writeln!(out, "(DIRECTION \"{DIRECTION}\")").unwrap();
    writeln!(out, "(DESIGN \"{module}\")").unwrap();
    writeln!(out, "(DATE \"{}\")", timestamp()).unwrap();
    writeln!(out, "(VENDOR \"{VENDOR}\")").unwrap();
    writeln!(out, "(PROGRAM_NAME \"{PROGRAM_NAME}\")").unwrap();
    writeln!(out, "(VERSION \"{VERSION}\")").unwrap();
    writeln!(out, "(DIVIDER {DIVIDER} )").unwrap();
    writeln!(out, "(TIMESCALE {TIMESCALE})").unwrap();
    writeln!(out, "(DURATION {duration})").unwrap();

    level = 0;
    let mut text_lvl = 0;
    for line in read_lines(vcd) {
        let line = line.unwrap();
        if let Some(cap) = re_scope.captures(&line) {
            let name = &cap[1];
            writeln!(out, "{}(INSTANCE {}", indent(text_lvl), name).unwrap();
            text_lvl += 1;
            level += 1;
            writeln!(out, "{}(NET", indent(text_lvl)).unwrap();
            text_lvl += 1;
            for v in &vars {
                if v.parent == *name && v.level == level {
                    let sig = if !v.multi_bit {
                        format!("{}", v.name)
                    } else {
                        format!("{}\\[{}\\]", v.name, v.bit_index)
                    };
                    writeln!(out, "{}({}", indent(text_lvl), sig).unwrap();
                    writeln!(
                        out,
                        "{}  (T0 {}) (T1 {}) (TX {})",
                        indent(text_lvl),
                        v.low,
                        v.high,
                        v.x
                    )
                    .unwrap();
                    writeln!(out, "{}  (TC {}) (IG {})", indent(text_lvl), v.toggle, v.ig).unwrap();
                    writeln!(out, "{})", indent(text_lvl)).unwrap();
                }
            }
            text_lvl -= 1;
            writeln!(out, "{})", indent(text_lvl)).unwrap();
        } else if re_up.is_match(&line) {
            text_lvl = text_lvl.saturating_sub(1);
            level = level.saturating_sub(1);
            writeln!(out, "{})", indent(text_lvl)).unwrap();
        }
    }
    writeln!(out, ")").unwrap();
}
