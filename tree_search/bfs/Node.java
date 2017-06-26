package bfs_tilescope;

import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;

/**
 * The nodes of a universe.
 *
 * @author Michael Albert
 */
class Node {

    static int ID = 0;
    static HashMap<Integer, Node> map = new HashMap<>();

    int id;
    Collection<Collection<Node>> productions = new HashSet<>();
    Collection<Node> parents = new HashSet<>();
    Collection<Node> remoteChildren = new HashSet<>();
    Collection<Collection<Node>> removedProductions = new HashSet<>();

    public Node() {
        this.id = ID;
        ID++;
        map.put(this.id, this);
    }

    Node(int source) {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    void addProduction(Collection<Node> production) {
        productions.add(production);
        for (Node n : production) {
            n.addParent(this);
        }
    }

    boolean hasNoProductions() {
        return productions.isEmpty();
    }

    Collection<Node> parents() {
        return parents;
    }

    void informRemote(Node s) {
        remoteChildren.add(s);
        if (!productions.isEmpty()) {
            for (Collection<Node> p : productions) {
                if (p.contains(s)) {
                    removedProductions.add(p);
                }
            }
            productions.removeAll(removedProductions);
        }
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

    private void addParent(Node p) {
        parents.add(p);
    }

    Collection<Node> getProduction() {
        for(Collection<Node> p : productions) {
            return p;
        }
        return null;
    }

}
