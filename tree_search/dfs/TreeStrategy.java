package verification;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;

/**
 * The strategy for building a verification tree for a node
 *
 * @author Michael Albert
 */
public class TreeStrategy {

    Node[] nodes;
    Node root;

    HashMap<Node, ArrayList<Node>> verification = new HashMap<>();
    Deque<Node> activeLeaves = new ArrayDeque<Node>();
    HashSet<Node> verifiedNodes = new HashSet<>();
    HashSet<Node> unusableNodes = new HashSet<>();

    public TreeStrategy(Node root, Node[] nodes) {
        this.nodes = nodes;
        this.root = root;
        for (Node n : nodes) {
            if (n.isVerified) {
                verifiedNodes.add(n);
                verification.put(n, n.verifier);
            } else if (n.isUnverifiable()) {
                unusableNodes.add(n);
            }
        }
    }

    public boolean run() {
        HashSet<Node> usable = new HashSet<Node>();
        return verify(root, usable);
    }
    
    public HashMap<Node, ArrayList<Node>> getVerification() {
        return verification;
    }

    private boolean verify(Node n, HashSet<Node> usable) {
        // System.out.println("Verifying " + n);
        if (n.isVerified || verifiedNodes.contains(n)) {
            // System.out.println("Verified " + n);
            return true;
        }
             
        if (unusableNodes.contains(n)) {
            // System.out.println("Unusable " + n);
            return false;
        }
        
        if (usable.contains(n)) {
            // System.out.println("Usable " + n);
            return true;
        }
        
        HashSet<Node> newUsable = (HashSet<Node>) usable.clone();
        newUsable.add(n);
        for(ArrayList<Node> witness : n.witnesses) {
            boolean good = true;
            for(Node w : witness) {
                good &= verify(w, newUsable);
                if (!good) break;
            }
            if (good) {
                verification.put(n, witness);
                return true;
            }
        }
        // System.out.println("Failed " + n);
        verifiedNodes.remove(n);
        unusableNodes.add(n);
        verification.remove(n);
        return false;
    }
}

