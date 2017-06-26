package verification;

import java.util.ArrayList;

/**
 * Represents a node in a verification tree.
 *
 * @author Michael Albert
 */
public class Node {

    static int nextId = 0;

    int id;
    boolean isVerified;
    ArrayList<Node> verifier;
    // No witnesses means 'unverifiable'
    // Having an empty witness means 'verified directly'
    ArrayList<ArrayList<Node>> witnesses;

    public Node() {
        id = nextId;
        nextId++;
        isVerified = false;
        verifier = null;
        witnesses = new ArrayList<>();
    }

    public void addWitness(ArrayList<Node> witness) {
        this.witnesses.add(witness);
    }

    public boolean isUnverifiable() {
        return witnesses.isEmpty();
    }

    public boolean update() {
        if (isVerified || isUnverifiable()) {
            return false;
        }
        
        ArrayList<ArrayList<Node>> toRemove = new ArrayList<>();
        for (ArrayList<Node> witness : witnesses) {
            if (allVerified(witness)) {
                verifier = witness;
                isVerified = true;
                return true;
            } else {
              if (someUnverifiable(witness)) toRemove.add(witness);
            }
        }
        
        if (!toRemove.isEmpty()) {
            for(ArrayList<Node> witness : toRemove) {
                witnesses.remove(witness);
            }
            return true;
        }
        
        
            
        return false;
    }

    private boolean allVerified(ArrayList<Node> witness) {
        for (Node w : witness) {
            if (!w.isVerified) {
                return false;
            }
        }
        return true;
    }

    @Override
    public int hashCode() {
        return this.id;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final Node other = (Node) obj;
        return this.id == other.id;
    }

    public ArrayList<ArrayList<Integer>> witnessIDs() {
        ArrayList<ArrayList<Integer>> result = new ArrayList<>();
        for (ArrayList<Node> witness : witnesses) {
            ArrayList<Integer> wid = new ArrayList<>();
            for (Node w : witness) {
                wid.add(w.id);
            }
            result.add(wid);
        }
        return result;
    }

    public ArrayList<Integer> verifierIDs() {
        if (verifier == null) {
            return null;
        }
        ArrayList<Integer> result = new ArrayList<>();
        for (Node v : verifier) {
            result.add(v.id);
        }
        return result;
    }

    @Override
    public String toString() {
        StringBuilder result = new StringBuilder();
        result.append(id + ": ");
        if (isVerified) {
            result.append(verifierIDs());
        } else {
            result.append("not verified");
            // result.append(witnessIDs());
        }
        // result.append("}");
        return result.toString();
//        return " " + id + " ";
    }

    private boolean someUnverifiable(ArrayList<Node> witness) {
        for(Node w: witness) {
            if (w.isUnverifiable()) return true;
        }
        return false;
    }

}
