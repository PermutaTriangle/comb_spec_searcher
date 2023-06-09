#[derive(Clone, Debug, PartialEq, Eq)]
pub enum IntOrInf {
    Int(u8),
    Infinity,
}

impl IntOrInf {
    pub fn is_finite(&self) -> bool {
        match self {
            IntOrInf::Int(_) => true,
            IntOrInf::Infinity => false,
        }
    }

    pub fn is_infinite(&self) -> bool {
        !self.is_finite()
    }
}

/// A representation of a function from N to N U {∞}
///
/// The default value of th function is 0.
pub struct Function {
    values: Vec<IntOrInf>,
    preimage_count: Vec<u32>,
    infinity_count: u32,
}

impl Function {
    pub fn new() -> Function {
        Function {
            values: vec![],
            preimage_count: vec![],
            infinity_count: 0,
        }
    }

    /// Get the current function value for the given input
    pub fn get_value(&self, input: u32) -> &IntOrInf {
        self.values.get(input as usize).unwrap_or(&IntOrInf::Int(0))
    }

    /// Increase by one the value of the function for the given input.
    pub fn increase_value(&mut self, input: u32) {
        let old_value = self.values.get_mut(input as usize);
        match old_value {
            Some(IntOrInf::Int(value)) => {
                self.preimage_count[*value as usize] -= 1;
                *value += 1;
                if self.preimage_count.len() <= *value as usize {
                    self.preimage_count.resize(*value as usize + 1, 0);
                }
                self.preimage_count[*value as usize] += 1;
            }
            Some(IntOrInf::Infinity) => (),
            None => {
                if self.preimage_count.len() < 2 {
                    self.preimage_count.resize(2, 0);
                }
                self.preimage_count[0] += input - self.values.len() as u32;
                self.preimage_count[1] += 1;
                self.values.resize(input as usize, IntOrInf::Int(0));
                self.values.push(IntOrInf::Int(1));
            }
        }
    }

    /// Set the value to infinity for the given input
    pub fn set_infinite(&mut self, input: u32) {
        let old_value = self.values.get_mut(input as usize);
        match old_value {
            Some(IntOrInf::Int(value)) => {
                self.preimage_count[*value as usize] -= 1;
                self.infinity_count += 1;
                *old_value.unwrap() = IntOrInf::Infinity;
            }
            Some(IntOrInf::Infinity) => (),
            None => {
                self.preimage_count[0] += input - self.values.len() as u32;
                self.preimage_count.resize(2, 0);
                self.preimage_count[1] += 1;
                self.values.resize(input as usize, IntOrInf::Int(0));
                self.values.push(IntOrInf::Int(1));
            }
        }
    }

    /// Number of value for which a value is registered
    pub fn len(&self) -> u32 {
        self.values.len() as u32
    }

    /// Return the preimage of the given input
    ///
    /// # Panic
    ///
    /// This function will panic on a value of 0 as the preimage is not well
    /// defined.
    pub fn preimage(&self, value: IntOrInf) -> FunctionPreImageIterator {
        match value {
            IntOrInf::Int(0) => panic!("The preimage of 0 is infinite"),
            _ => FunctionPreImageIterator::new(self, value),
        }
    }

    /// Return the smallest k such that the preimage of the interval
    /// [k, k+length-1] is empty.
    ///
    /// # Panic
    ///
    /// This function will panic on a gap size of 0 gap is not well defined.
    pub fn preimage_gap(&self, gap_size: u32) -> u32 {
        if gap_size == 0 {
            panic!("Gap of size 0 is not well defined.");
        }
        let mut last_non_zero: u32 = 0;
        for (i, v) in self.preimage_count.iter().enumerate() {
            if *v != 0 {
                last_non_zero = i as u32;
            } else if i as u32 - last_non_zero >= gap_size {
                return last_non_zero + 1;
            }
        }
        last_non_zero + 1
    }

    pub fn get_infinity_count(&self) -> u32 {
        self.infinity_count
    }

    pub fn get_preimage_count(&self) -> &Vec<u32> {
        &self.preimage_count
    }
}

pub struct FunctionPreImageIterator<'a> {
    function: &'a Function,
    value: IntOrInf,
    pos: u32,
}

impl<'a> FunctionPreImageIterator<'a> {
    fn new(function: &Function, value: IntOrInf) -> FunctionPreImageIterator {
        FunctionPreImageIterator {
            function,
            value,
            pos: 0,
        }
    }
}

impl<'a> Iterator for FunctionPreImageIterator<'a> {
    type Item = u32;

    fn next(&mut self) -> Option<u32> {
        while self.pos < self.function.len() {
            let value_for_pos = self.function.get_value(self.pos);
            self.pos += 1;
            if *value_for_pos == self.value {
                return Some(self.pos as u32 - 1);
            }
        }
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn create_function() {
        let mut f = Function::new();
    }

    #[test]
    fn add_value() {
        let mut f = Function::new();
        assert_eq!(*f.get_value(0), IntOrInf::Int(0));
        assert_eq!(*f.get_value(0), IntOrInf::Int(0));
        f.increase_value(0);
        assert_eq!(*f.get_value(0), IntOrInf::Int(1));
        f.increase_value(3);
        assert_eq!(*f.get_value(4), IntOrInf::Int(0));
        f.increase_value(4);
        assert_eq!(*f.get_value(0), IntOrInf::Int(1));
        assert_eq!(*f.get_value(1), IntOrInf::Int(0));
        assert_eq!(*f.get_value(2), IntOrInf::Int(0));
        assert_eq!(*f.get_value(3), IntOrInf::Int(1));
        assert_eq!(*f.get_value(4), IntOrInf::Int(1));
        assert_eq!(*f.get_value(5), IntOrInf::Int(0));
        assert_eq!(*f.get_value(6), IntOrInf::Int(0));
    }

    #[test]
    fn preimage() {
        let mut f = Function::new();
        f.increase_value(0);
        f.increase_value(3);
        f.increase_value(4);
        let mut preimage1: Vec<_> = f.preimage(IntOrInf::Int(1)).collect();
        preimage1.sort();
        assert_eq!(preimage1, vec![0, 3, 4]);
        assert_eq!(f.preimage(IntOrInf::Int(2)).count(), 0);
    }

    #[test]
    #[should_panic(expected = "The preimage of 0 is infinite")]
    fn preimage_0() {
        let mut f = Function::new();
        f.increase_value(0);
        f.increase_value(3);
        f.increase_value(4);
        f.preimage(IntOrInf::Int(0));
    }

    #[test]
    fn infinity() {
        let mut f = Function::new();
        f.increase_value(0);
        f.increase_value(3);
        f.increase_value(4);
        f.set_infinite(3);
        assert_eq!(*f.get_value(0), IntOrInf::Int(1));
        assert_eq!(*f.get_value(1), IntOrInf::Int(0));
        assert_eq!(*f.get_value(2), IntOrInf::Int(0));
        assert_eq!(*f.get_value(3), IntOrInf::Infinity);
        assert_eq!(*f.get_value(4), IntOrInf::Int(1));
    }

    #[test]
    fn preimage_inf() {
        let mut f = Function::new();
        f.increase_value(0);
        f.increase_value(3);
        f.increase_value(4);
        f.set_infinite(3);
        assert_eq!(f.preimage(IntOrInf::Infinity).collect::<Vec<_>>(), vec![3]);
        let mut preimage1: Vec<_> = f.preimage(IntOrInf::Int(1)).collect();
        preimage1.sort();
        assert_eq!(preimage1, vec![0, 4]);
    }

    #[test]
    fn bug() {
        let mut f = Function::new();
        f.increase_value(1);
        println!("{:?}", f.preimage_count);
        f.increase_value(1);
        println!("{:?}", f.preimage_count);
        f.increase_value(1);
        println!("{:?}", f.preimage_count);
        f.increase_value(5);
        println!("{:?}", f.preimage_count);
        f.increase_value(5);
        println!("{:?}", f.preimage_count);
        f.increase_value(4);
        println!("{:?}", f.preimage_count);
        f.increase_value(5);
        println!("{:?}", f.preimage_count);
    }

    #[test]
    fn preimage_count() {
        let mut f = Function::new();
        f.increase_value(0);
        assert_eq!(f.preimage_count, vec![0, 1]);
        f.increase_value(0);
        assert_eq!(f.preimage_count, vec![0, 0, 1]);
        f.increase_value(0);
        assert_eq!(f.preimage_count, vec![0, 0, 0, 1]);
        f.increase_value(0);
        assert_eq!(f.preimage_count, vec![0, 0, 0, 0, 1]);
        f.increase_value(1);
        assert_eq!(f.preimage_count, vec![0, 1, 0, 0, 1]);
        f.increase_value(2);
        assert_eq!(f.preimage_count, vec![0, 2, 0, 0, 1]);
    }

    #[test]
    fn preimage_gap_inf() {
        let mut f = Function::new();
        f.increase_value(0);
        f.increase_value(3);
        f.increase_value(4);
        f.set_infinite(3);
        assert_eq!(f.preimage_gap(100), 2);
    }

    #[test]
    fn find_gap() {
        let mut f = Function::new();
        f.increase_value(0);
        f.increase_value(0);
        f.increase_value(0);
        f.increase_value(0);
        f.increase_value(1);
        f.increase_value(2);
        assert_eq!(*f.get_value(0), IntOrInf::Int(4));
        assert_eq!(*f.get_value(1), IntOrInf::Int(1));
        assert_eq!(*f.get_value(2), IntOrInf::Int(1));
        assert_eq!(*f.get_value(3), IntOrInf::Int(0));
        assert_eq!(*f.get_value(4), IntOrInf::Int(0));
        assert_eq!(*f.get_value(5), IntOrInf::Int(0));
        assert_eq!(*f.get_value(6), IntOrInf::Int(0));
        assert_eq!(f.preimage_gap(1), 2);
        assert_eq!(f.preimage_gap(2), 2);
        assert_eq!(f.preimage_gap(3), 5);
    }

    #[test]
    #[should_panic(expected = "0")]
    fn find_size_zero_gap() {
        let f = Function::new();
        f.preimage_gap(0);
    }

    #[test]
    fn find_gap2() {
        let mut f = Function::new();
        f.increase_value(2);
        f.increase_value(3);
        f.increase_value(4);
        f.increase_value(5);
        f.increase_value(5);
        f.increase_value(5);
        assert_eq!(*f.get_value(0), IntOrInf::Int(0));
        assert_eq!(*f.get_value(1), IntOrInf::Int(0));
        assert_eq!(*f.get_value(2), IntOrInf::Int(1));
        assert_eq!(*f.get_value(3), IntOrInf::Int(1));
        assert_eq!(*f.get_value(4), IntOrInf::Int(1));
        assert_eq!(*f.get_value(5), IntOrInf::Int(3));
        assert_eq!(f.preimage_gap(1), 2);
        assert_eq!(f.preimage_gap(2), 4);
        assert_eq!(f.preimage_gap(3), 4);
    }
}
