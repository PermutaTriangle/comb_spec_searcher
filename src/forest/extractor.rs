use super::ForestRuleKey;
use super::RuleBucket;
use super::table_method::TableMethod;
use std::collections::HashSet;

const MINIMIZE_ORDER: [RuleBucket; 4] = [
    RuleBucket::Reverse,
    RuleBucket::Normal,
    RuleBucket::Equiv,
    RuleBucket::Verification,
];

enum MinimizationRoundResult {
    Done(TableMethod),
    NotDone(TableMethod),
}

/// Perform one round of the minimization.
///
/// Insert into the table method until it pumps for the root class add the last
/// rule to the maybe useful set.
fn minimzation_bucket_round(
    tb: TableMethod,
    bucket: &RuleBucket,
    root_class: u32,
    maybe_useful: &mut HashSet<ForestRuleKey>,
) -> MinimizationRoundResult {
    let mut new_tb = TableMethod::new();
    let mut rules_in_bucket = vec![];
    for rk in tb.into_pumping_subuniverse() {
        if rk.get_bucket() == bucket && !maybe_useful.contains(&rk) {
            rules_in_bucket.push(rk);
        } else {
            new_tb.add_rule_key(rk);
        }
    }
    if new_tb.is_pumping(root_class) {
        return MinimizationRoundResult::Done(new_tb);
    }
    while !new_tb.is_pumping(root_class) {
        let last_key = new_tb.add_rule_key(
            rules_in_bucket
                .pop()
                .expect("Not pumping after adding all rules"),
        );
        maybe_useful.insert(last_key.clone());
    }
    MinimizationRoundResult::NotDone(new_tb)
}

/// Minimize the rules for a given bucket
fn minimize_bucket(mut tb: TableMethod, bucket: &RuleBucket, root_class: u32) -> TableMethod {
    let mut done = false;
    let mut maybe_useful = HashSet::new();
    while !done {
        (tb, done) = match minimzation_bucket_round(tb, bucket, root_class, &mut maybe_useful) {
            MinimizationRoundResult::Done(tb) => (tb, true),
            MinimizationRoundResult::NotDone(tb) => (tb, false),
        }
    }
    tb
}

/// Perform the complete minimization of the forest
fn minimize(tb: TableMethod, root_class: u32) -> TableMethod {
    let mut tb = tb;
    for bucket in MINIMIZE_ORDER.iter() {
        tb = minimize_bucket(tb, bucket, root_class);
    }
    tb
}

pub fn extract_specification(root_class: u32, tb: TableMethod) -> Vec<ForestRuleKey> {
    let minimized = minimize(tb, root_class);
    let rules: Vec<_> = minimized.into_rules().collect();
    let parents: HashSet<_> = rules.iter().map(|rk| rk.get_parent()).collect();
    assert_eq!(parents.len(), rules.len());
    for rk in rules.iter() {
        for c in rk.iter_children() {
            assert!(parents.contains(c));
        }
    }
    rules
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn extract_132_test() {
        let rules = vec![
            ForestRuleKey::new(0, vec![1, 2], vec![0, 0], RuleBucket::Normal),
            ForestRuleKey::new(1, vec![], vec![], RuleBucket::Verification),
            ForestRuleKey::new(2, vec![3], vec![0], RuleBucket::Equiv),
            ForestRuleKey::new(3, vec![4], vec![0], RuleBucket::Equiv),
            ForestRuleKey::new(4, vec![5, 0, 0], vec![0, 1, 1], RuleBucket::Normal),
            ForestRuleKey::new(5, vec![], vec![], RuleBucket::Verification),
            ForestRuleKey::new(2, vec![6], vec![2], RuleBucket::Undefined),
        ];
        let mut tb = TableMethod::new();
        for rule in rules.into_iter() {
            tb.add_rule_key(rule);
        }
        let spec = extract_specification(0, tb);
        assert_eq!(spec.len(), 6);
    }
}
