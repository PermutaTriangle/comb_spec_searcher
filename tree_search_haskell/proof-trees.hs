import Data.List
import Data.Tree
import Data.IntMap.Strict (IntMap, (!))
import qualified Data.IntMap.Strict as M
import Data.IntSet (IntSet, member)
import qualified Data.IntSet as S
import System.Environment (getArgs)

type ProofTree = Tree Int

data Table = Table
    { sup  :: Int
    , root :: Int
    , rule :: IntMap [[Int]]
    } deriving Show

parseTable :: String -> Table
parseTable s = Table
    { sup  = read supStr
    , root = read rootStr
    , rule = M.fromListWith (++) [ (x, [xs]) | row <- rules, let x:xs = read <$> words row ]
    }
  where
    supStr : rootStr : rules = filter (not . null) (lines s)

readTable :: String -> IO Table
readTable path = parseTable <$> readFile path

-- Prune all unverifiable nodes (recursively)
prune :: Table -> Table
prune table = prune' $ table {rule = rule'}
  where
    prune' = if rule' == rule table then id else prune
    rule' = M.mapMaybe f (rule table)
    vs = [0 .. sup table] \\ M.keys (rule table) -- Unverifiable nodes
    f [[]] = Just [[]]
    f uss = let uss' = [ us | us <- uss, null (us `intersect` vs) ]
            in if null uss' then Nothing else Just uss'

proofTrees :: IntSet -> Table -> [(IntSet, ProofTree)]
proofTrees seen table =
    if M.notMember v (rule table)
    then []
    else if rss == [[]] || v `member` seen
         then [ (seen',  Node v []) ]
         else do
           rs <- rss
           (seen'', ts) <- proofForests seen' table rs
           return (seen'', Node v ts)
  where
    v = root table
    rss = rule table ! v
    seen' = S.insert v seen

proofForests :: IntSet -> Table -> [Int] -> [(IntSet, [ProofTree])]
proofForests seen table [] = [(seen, [])]
proofForests seen table (r:rs) = do
    (seen', t) <- proofTrees seen (table {root = r})
    (seen'', ts) <- proofForests seen' table rs
    return (S.union seen' seen'', t:ts)

printProofTrees :: String -> Int -> IO ()
printProofTrees fname n = do
    table <- readTable fname
    let trees = map snd (proofTrees S.empty (prune table))
    mapM_ (putStrLn . drawTree . fmap show) (take n trees)

main = do
    args <- getArgs
    case args of
      [] -> putStrLn "usage: ./proof-trees file_name [max_number_of_trees]"
      [fname] -> printProofTrees fname 1
      (fname:n:_) -> printProofTrees fname (read n)
