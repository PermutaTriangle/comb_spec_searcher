use super::{Function, IntOrInf};
use std::collections::hash_map::DefaultHasher;

use core::slice::Iter;
use pyo3::class::basic::CompareOp;
use pyo3::prelude::*;
use pyo3::types::PyTuple;
use std;
use std::collections::{HashMap, HashSet, VecDeque};
use std::hash::{Hash, Hasher};

#[pyclass]
#[derive(Debug, PartialEq, Eq, Hash, Clone)]
pub enum RuleBucket {
    #[pyo3(name = "UNDEFINED")]
    Undefined,
    #[pyo3(name = "VERIFICATION")]
    Verification,
    #[pyo3(name = "EQUIV")]
    Equiv,
    #[pyo3(name = "NORMAL")]
    Normal,
    #[pyo3(name = "REVERSE")]
    Reverse,
}

#[pymethods]
impl RuleBucket {
    fn __hash__(&self) -> u64 {
        match self {
            RuleBucket::Undefined => 0,
            RuleBucket::Verification => 1,
            RuleBucket::Equiv => 2,
            RuleBucket::Normal => 3,
            RuleBucket::Reverse => 4,
        }
    }

    #[getter]
    fn get_name(&self) -> &str {
        match self {
            RuleBucket::Undefined => "UNDEFINED",
            RuleBucket::Verification => "VERIFICATION",
            RuleBucket::Equiv => "EQUIV",
            RuleBucket::Normal => "NORMAL",
            RuleBucket::Reverse => "REVERSE",
        }
    }
}

struct RuleClassConnector {
    rule_using_class: HashMap<u32, Vec<(usize, usize)>>,
    rule_pumping_class: HashMap<u32, Vec<usize>>,
}

impl RuleClassConnector {
    pub fn new() -> RuleClassConnector {
        RuleClassConnector {
            rule_using_class: HashMap::new(),
            rule_pumping_class: HashMap::new(),
        }
    }

    pub fn add_rule_pumping_class(&mut self, class: u32, rule_idx: usize) {
        let entry = self.rule_pumping_class.entry(class).or_insert(vec![]);
        entry.push(rule_idx);
    }

    pub fn add_rule_using_class(&mut self, class: u32, rule_idx: usize, child_idx: usize) {
        let entry = self.rule_using_class.entry(class).or_insert(vec![]);
        entry.push((rule_idx, child_idx));
    }

    pub fn get_rules_pumping_class(&self, class: u32) -> impl Iterator<Item = &usize> {
        self.rule_pumping_class
            .get(&class)
            .map(|v| v.iter())
            .unwrap_or([][..].iter())
    }

    pub fn get_rules_using_class(&self, class: u32) -> impl Iterator<Item = &(usize, usize)> {
        self.rule_using_class
            .get(&class)
            .map(|v| v.iter())
            .unwrap_or([][..].iter())
    }

    pub fn remove_class_information(&mut self, class: u32) {
        todo!("This implementation is not correct");
        self.rule_using_class.remove(&class);
        self.rule_pumping_class.remove(&class);
    }
}

#[pyclass]
#[derive(Debug, Hash, Clone, PartialEq, Eq)]
pub struct ForestRuleKey {
    #[pyo3(get)]
    parent: u32,
    children: Vec<u32>,
    shifts: Vec<i8>,
    #[pyo3(get)]
    bucket: RuleBucket,
}

impl ForestRuleKey {
    pub fn new(
        parent: u32,
        children: Vec<u32>,
        shifts: Vec<i8>,
        bucket: RuleBucket,
    ) -> ForestRuleKey {
        ForestRuleKey {
            parent,
            children,
            shifts,
            bucket,
        }
    }

    pub fn key(&self) -> (&u32, &Vec<u32>) {
        (&self.parent, &self.children)
    }

    pub fn get_bucket(&self) -> &RuleBucket {
        &self.bucket
    }

    pub fn get_parent(&self) -> &u32 {
        &self.parent
    }

    pub fn iter_children(&self) -> Iter<u32> {
        self.children.iter()
    }
}

#[pymethods]
impl ForestRuleKey {
    #[new]
    fn py_new(parent: u32, children: Vec<u32>, shifts: Vec<i8>, bucket: RuleBucket) -> Self {
        ForestRuleKey::new(parent, children, shifts, bucket)
    }

    #[getter]
    fn get_key(&self, py: Python<'_>) -> (u32, Py<PyTuple>) {
        (self.parent, self.get_children(py))
    }

    #[getter]
    fn get_children(&self, py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, self.children.clone()).into()
    }

    #[getter]
    fn get_shifts(&self, py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, self.shifts.clone()).into()
    }

    fn __richcmp__(&self, other: &Self, op: CompareOp, py: Python<'_>) -> PyObject {
        match op {
            CompareOp::Eq => (self == other).into_py(py),
            CompareOp::Ne => (self != other).into_py(py),
            _ => py.NotImplemented(),
        }
    }

    fn __hash__(&self) -> u64 {
        let mut s = DefaultHasher::new();
        self.hash(&mut s);
        s.finish()
    }
}

#[pyclass]
pub struct TableMethod {
    rules: Vec<ForestRuleKey>,
    shifts: Vec<Vec<Option<i8>>>,
    function: Function,
    gap_size: u32,
    // Both for rule using and rule pumping class
    rule_class_connector: RuleClassConnector,
    processing_queue: VecDeque<usize>,
    current_gap: (u32, u32),
    rule_holding_extra_terms: HashSet<usize>,
}

impl TableMethod {
    pub fn new() -> TableMethod {
        TableMethod {
            rules: vec![],
            shifts: vec![],
            function: Function::new(),
            gap_size: 1,
            rule_class_connector: RuleClassConnector::new(),
            processing_queue: VecDeque::new(),
            current_gap: (1, 1),
            rule_holding_extra_terms: HashSet::new(),
        }
    }

    /// Add the rule to the database
    pub fn add_rule_key(&mut self, rule_key: ForestRuleKey) -> &ForestRuleKey {
        self.rules.push(rule_key);
        let rule_key = self.rules.last().unwrap();
        self.shifts.push(self.compute_shift(&rule_key));
        let max_gap = rule_key.shifts.iter().map(|s| s.abs()).max().unwrap_or(0) as u32;
        if max_gap > self.gap_size {
            self.gap_size = max_gap;
            self.correct_gap();
        }
        // Because the correct gap need a mutable reference to self we need to
        // invalidate the immutable reference hold by rule_key.
        let rule_key = self.rules.last().unwrap();
        if self.function.get_value(rule_key.parent).is_finite() {
            let rule_idx = self.rules.len() - 1;
            self.rule_class_connector
                .add_rule_pumping_class(rule_key.parent, rule_idx);
            for (child_idx, child) in rule_key.children.iter().enumerate() {
                if self.function.get_value(*child).is_finite() {
                    self.rule_class_connector
                        .add_rule_using_class(*child, rule_idx, child_idx);
                }
            }
            self.processing_queue.push_back(rule_idx);
        }
        self.process_queue();
        let rule_key = self.rules.last().unwrap();
        rule_key
    }

    /// Determine if the comb_class is pumping in the current universe.
    pub fn is_pumping(&self, class: u32) -> bool {
        self.function.get_value(class).is_infinite()
    }

    pub fn stable_subset(&self) -> impl Iterator<Item = u32> + '_ {
        self.function.preimage(IntOrInf::Infinity)
    }

    /// Iterator over all the forest rule keys that contain only pumping
    /// combinatorial classes.
    pub fn pumping_subuniverse(&self) -> impl Iterator<Item = &ForestRuleKey> {
        self.rules.iter().filter(move |forest_key| {
            self.is_pumping(forest_key.parent)
                && forest_key.children.iter().all(|c| self.is_pumping(*c))
        })
    }

    /// Consumes the self and iterate all the forest rule keys that contain only pumping
    /// combinatorial classes.
    pub fn into_pumping_subuniverse(self) -> impl Iterator<Item = ForestRuleKey> {
        let stable_subset: HashSet<_> = self.stable_subset().collect();
        self.rules.into_iter().filter(move |forest_key| {
            stable_subset.contains(&forest_key.parent)
                && forest_key
                    .children
                    .iter()
                    .all(|c| stable_subset.contains(c))
        })
    }

    /// Consumes self and returns all the forest rule keys it contains.
    pub fn into_rules(self) -> impl Iterator<Item = ForestRuleKey> {
        self.rules.into_iter()
    }

    pub fn status(&self) -> String {
        let mut s = String::new();
        s += &format!("\tSize of the gap: {}\n", self.gap_size);
        s += &format!("\tSize of the stable subset: {}\n", self.function.get_infinity_count());
        s += &format!("\tSizes of the pre-images: {:?}\n", self.function.get_preimage_count());
        s
    }

    /// Compute the initial value for the shifts a rule based on the current state of
    /// the function.
    fn compute_shift(&self, rule_key: &ForestRuleKey) -> Vec<Option<i8>> {
        let parent_curent_value = self.function.get_value(rule_key.parent);
        match parent_curent_value {
            IntOrInf::Infinity => vec![None; rule_key.children.len()],
            IntOrInf::Int(parent_curent_value) => {
                let children_function_values = rule_key
                    .children
                    .iter()
                    .map(|c| self.function.get_value(*c));
                children_function_values
                    .zip(&rule_key.shifts)
                    .map(|(fvalue, sfz)| match fvalue {
                        IntOrInf::Infinity => None,
                        IntOrInf::Int(fvalue) => {
                            Some(*fvalue as i8 + sfz - *parent_curent_value as i8)
                        }
                    })
                    .collect()
            }
        }
    }

    /// Correct the gap and if needed queue rules for the classes that were previously
    /// on the right hand  side of the gap.
    ///
    /// This should be toggled every time the gap changes whether the size changes or
    /// some value changes of the function caused the gap to change.
    fn correct_gap(&mut self) {
        let k = self.function.preimage_gap(self.gap_size);
        let new_gap = (k, k + self.gap_size);
        if new_gap.1 > self.current_gap.1 {
            self.processing_queue
                .extend(self.rule_holding_extra_terms.iter());
            self.rule_holding_extra_terms.clear();
        }
        self.current_gap = new_gap;
    }

    /// Try to make improvement with all the class in the processing queue.
    fn process_queue(&mut self) {
        while !self.processing_queue.is_empty() || !self.rule_holding_extra_terms.is_empty() {
            while let Some(rule_idx) = self.processing_queue.pop_front() {
                let shifts = self.shifts.get(rule_idx).unwrap();
                if TableMethod::can_give_terms(shifts) {
                    let parent = self.rules[rule_idx].parent;
                    self.increase_value(parent, rule_idx);
                }
            }
            if let Some(&rule_idx) = self.rule_holding_extra_terms.iter().next() {
                self.rule_holding_extra_terms.remove(&rule_idx);
                let parent = self.rules[rule_idx].parent;
                self.set_infinite(parent);
            }
        }
    }

    /// Return true if the shifts indicate that a new term can be computed
    fn can_give_terms(shifts: &Vec<Option<i8>>) -> bool {
        shifts.iter().all(|&s| s.map_or(true, |x| x > 0))
    }

    /// Increase the value of the comb_class and put on the processing stack any rule
    /// that can now give a new term.
    ///
    ///The rule_idx must indicate the rule used to justify the increase.
    fn increase_value(&mut self, class: u32, rule_idx: usize) {
        let current_value = self.function.get_value(class);
        let current_value = match current_value {
            IntOrInf::Infinity => return,
            IntOrInf::Int(v) => *v,
        };
        if current_value as u32 > self.current_gap.1 {
            self.rule_holding_extra_terms.insert(rule_idx);
            return;
        }
        self.function.increase_value(class);
        // Correction of the gap
        let gap_start = self.function.preimage_gap(self.gap_size);
        if self.current_gap.0 != gap_start {
            self.correct_gap()
        }
        // Correction of shifts for rule pumping class
        for &r_idx in self.rule_class_connector.get_rules_pumping_class(class) {
            let shifts = self.shifts.get_mut(r_idx).unwrap();
            for v in shifts.iter_mut() {
                *v = v.map(|v| v - 1);
            }
            if TableMethod::can_give_terms(shifts) {
                self.processing_queue.push_back(r_idx)
            }
        }
        // Correction of the shifts for rule using the class
        for &(r_idx, class_idx) in self.rule_class_connector.get_rules_using_class(class) {
            let shifts = self.shifts.get_mut(r_idx).unwrap();
            let current_shift = shifts.get_mut(class_idx).unwrap();
            *current_shift = current_shift.map(|v| v + 1);
            if TableMethod::can_give_terms(shifts) {
                self.processing_queue.push_back(r_idx);
            }
        }
    }

    /// Set the value if the class to infinity.
    ///
    /// This should happen when we know that we cannot pump anything on the left side
    /// of the gap.
    fn set_infinite(&mut self, class: u32) {
        let current_value = self.function.get_value(class);
        let current_value = match current_value {
            IntOrInf::Infinity => return,
            IntOrInf::Int(v) => v,
        };
        assert!(*current_value as u32 > self.current_gap.1);
        assert!(self.processing_queue.is_empty());
        self.function.set_infinite(class);
        // This class will never be increased again so we remove any occurrence
        // of the rule of any rule for that class from _rules_using_class and
        //_rules_pumping_class
        // TODO: implement that later since its only for saving memory
        // for rule_idx in self._rules_pumping_class[comb_class]:
        //     for child in self._rules[rule_idx].children:
        //         self._rules_using_class[child] = [
        //             (ri, ci)
        //             for ri, ci in self._rules_using_class[child]
        //             if ri != rule_idx
        //         ]
        // self._rules_pumping_class[comb_class].clear()
        // Correction of the shifts for rules using comb_class to pump
        for &(rule_idx, class_idx) in self.rule_class_connector.get_rules_using_class(class) {
            let shifts = self.shifts.get_mut(rule_idx).unwrap();
            shifts[class_idx] = None;
            if TableMethod::can_give_terms(shifts) {
                self.processing_queue.push_back(rule_idx)
            }
        }
        // TODO: same as above
        // self._rules_using_class[comb_class].clear()
    }
}

#[pymethods]
impl TableMethod {
    #[new]
    fn py_new() -> Self {
        TableMethod::new()
    }

    #[pyo3(name="add_rule_key")]
    fn py_add_rule_key(&mut self, rule_key: ForestRuleKey) {
        self.add_rule_key(rule_key);
    }

    #[getter]
    fn get_function(&self) -> HashMap<u32, Option<u8>> {
        let mut map = HashMap::new();
        for pos in 0..self.function.len() {
            let value = self.function.get_value(pos);
            match value {
                IntOrInf::Infinity => {map.insert(pos, None);},
                IntOrInf::Int(0) => (),
                IntOrInf::Int(x) => {map.insert(pos, Some(*x));},
            }
        }
        map
    }

    #[pyo3(name="is_pumping")]
    fn py_is_pumping(&self, label: u32) -> bool {
        self.is_pumping(label)
    }

    #[pyo3(name="pumping_subuniverse")]
    fn py_pumping_subuniverse(&self) -> Vec<ForestRuleKey> {
        self.pumping_subuniverse().map(|rk| rk.clone()).collect()
    }

    #[pyo3(name="status")]
    fn py_status(&self) -> String {
        self.status()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The universe consist of the rule of the usual 132 tree plus a dummy rule that is
    /// useless.
    #[test]
    fn pumping_132_universe_test() {
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
        for i in 0..6 {
            assert_eq!(*tb.function.get_value(i), IntOrInf::Infinity)
        }
        assert!((0..6).all(|c| tb.is_pumping(c)));
        assert!(!tb.is_pumping(6));
        let mut pu: Vec<_> = tb
            .pumping_subuniverse()
            .map(|forest_key| forest_key.key())
            .collect();
        pu.sort();
        assert_eq!(
            pu,
            vec![
                (&0, &vec![1, 2]),
                (&1, &vec![]),
                (&2, &vec![3]),
                (&3, &vec![4]),
                (&4, &vec![5, 0, 0]),
                (&5, &vec![])
            ]
        );
    }

    /// The universe consist of the rule of the usual 132 tree plus a dummy rule that is
    /// useless.

    /// We add rule progressively and make sure the function is always up to date.
    #[test]
    fn universe132_pumping_progressive_test() {
        let mut tb = TableMethod::new();

        // Point insertion
        tb.add_rule_key(ForestRuleKey::new(
            0,
            vec![1, 2],
            vec![0, 0],
            RuleBucket::Normal,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Int(0));
        // Empty verif
        tb.add_rule_key(ForestRuleKey::new(
            1,
            vec![],
            vec![],
            RuleBucket::Verification,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(2), &IntOrInf::Int(0));
        // Point placement
        tb.add_rule_key(ForestRuleKey::new(2, vec![3], vec![0], RuleBucket::Equiv));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(2), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(0));
        // Row col sept
        tb.add_rule_key(ForestRuleKey::new(3, vec![4], vec![0], RuleBucket::Equiv));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(2), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Int(0));
        // Point verif
        tb.add_rule_key(ForestRuleKey::new(
            5,
            vec![],
            vec![],
            RuleBucket::Verification,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(2), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        // Dumb rule
        tb.add_rule_key(ForestRuleKey::new(
            2,
            vec![6],
            vec![-2],
            RuleBucket::Undefined,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(2), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(0));
        // Dumb rule. This will pump 2 and 0 a little bit
        tb.add_rule_key(ForestRuleKey::new(
            2,
            vec![7],
            vec![2],
            RuleBucket::Undefined,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(2), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(7), &IntOrInf::Int(0));
        // Factor
        tb.add_rule_key(ForestRuleKey::new(
            4,
            vec![5, 0, 0],
            vec![0, 1, 1],
            RuleBucket::Normal,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(1), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(3), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(4), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(7), &IntOrInf::Int(0));
    }

    #[test]
    fn universe_not_pumping_test() {
        let rules = vec![
            ForestRuleKey::new(0, vec![1, 2], vec![0, 0], RuleBucket::Normal),
            ForestRuleKey::new(5, vec![], vec![], RuleBucket::Verification),
            ForestRuleKey::new(2, vec![3], vec![0], RuleBucket::Normal),
            ForestRuleKey::new(3, vec![4], vec![0], RuleBucket::Normal),
            ForestRuleKey::new(4, vec![5, 0, 0], vec![0, 1, 1], RuleBucket::Normal),
        ];
        let mut tb = TableMethod::new();
        for rule in rules.into_iter() {
            tb.add_rule_key(rule);
        }
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Int(0));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
    }

    #[test]
    fn segmented_test() {
        let mut tb = TableMethod::new();

        tb.add_rule_key(ForestRuleKey::new(
            0,
            vec![1, 2],
            vec![0, 0],
            RuleBucket::Undefined,
        ));
        tb.add_rule_key(ForestRuleKey::new(
            1,
            vec![4, 14],
            vec![0, 0],
            RuleBucket::Undefined,
        ));
        tb.add_rule_key(ForestRuleKey::new(2, vec![], vec![], RuleBucket::Undefined));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);

        tb.add_rule_key(ForestRuleKey::new(
            3,
            vec![16, 5],
            vec![1, 0],
            RuleBucket::Undefined,
        ));
        tb.add_rule_key(ForestRuleKey::new(4, vec![], vec![], RuleBucket::Undefined));
        tb.add_rule_key(ForestRuleKey::new(5, vec![], vec![], RuleBucket::Undefined));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);

        // Induced a gap size change
        tb.add_rule_key(ForestRuleKey::new(
            6,
            vec![7, 5, 17],
            vec![2, 1, 1],
            RuleBucket::Undefined,
        ));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(1));

        tb.add_rule_key(ForestRuleKey::new(
            16,
            vec![6],
            vec![0],
            RuleBucket::Undefined,
        ));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(16), &IntOrInf::Int(1));

        tb.add_rule_key(ForestRuleKey::new(7, vec![], vec![], RuleBucket::Undefined));
        tb.add_rule_key(ForestRuleKey::new(
            8,
            vec![9, 5],
            vec![1, 0],
            RuleBucket::Undefined,
        ));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(7), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(8), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(16), &IntOrInf::Int(1));

        tb.add_rule_key(ForestRuleKey::new(
            12,
            vec![20, 5],
            vec![-1, 0],
            RuleBucket::Undefined,
        ));
        tb.add_rule_key(ForestRuleKey::new(
            20,
            vec![13],
            vec![0],
            RuleBucket::Undefined,
        ));
        tb.add_rule_key(ForestRuleKey::new(
            13,
            vec![15, 2, 5],
            vec![-1, 1, 0],
            RuleBucket::Undefined,
        ));
        tb.add_rule_key(ForestRuleKey::new(
            15,
            vec![1],
            vec![0],
            RuleBucket::Undefined,
        ));
        tb.add_rule_key(ForestRuleKey::new(
            14,
            vec![3],
            vec![0],
            RuleBucket::Undefined,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(7), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(8), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(13), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(14), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(15), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(16), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(20), &IntOrInf::Int(1));

        tb.add_rule_key(ForestRuleKey::new(
            18,
            vec![8],
            vec![0],
            RuleBucket::Undefined,
        ));
        tb.add_rule_key(ForestRuleKey::new(
            11,
            vec![12, 18],
            vec![0, 0],
            RuleBucket::Undefined,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(7), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(8), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(13), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(14), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(15), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(16), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(18), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(20), &IntOrInf::Int(1));

        tb.add_rule_key(ForestRuleKey::new(
            17,
            vec![8],
            vec![0],
            RuleBucket::Undefined,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(7), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(8), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(11), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(12), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(13), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(14), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(15), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(16), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(17), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(18), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(20), &IntOrInf::Int(2));

        tb.add_rule_key(ForestRuleKey::new(
            9,
            vec![0, 19],
            vec![0, 0],
            RuleBucket::Undefined,
        ));
        tb.add_rule_key(ForestRuleKey::new(
            10,
            vec![5, 11],
            vec![0, 1],
            RuleBucket::Undefined,
        ));
        assert_eq!(tb.function.get_value(0), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(1), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(2), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(3), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(4), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(5), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(6), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(7), &IntOrInf::Infinity);
        assert_eq!(tb.function.get_value(8), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(10), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(11), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(12), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(13), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(14), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(15), &IntOrInf::Int(3));
        assert_eq!(tb.function.get_value(16), &IntOrInf::Int(2));
        assert_eq!(tb.function.get_value(17), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(18), &IntOrInf::Int(1));
        assert_eq!(tb.function.get_value(20), &IntOrInf::Int(2));

        tb.add_rule_key(ForestRuleKey::new(
            19,
            vec![10],
            vec![0],
            RuleBucket::Undefined,
        ));
        assert!((0..21).all(|c| tb.function.get_value(c) == &IntOrInf::Infinity));
        assert!((0..21).all(|c| tb.is_pumping(c)));
    }
}
