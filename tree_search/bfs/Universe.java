package bfs_tilescope;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Scanner;

/**
 * A universe is a set of stars (implemented as a HashMap)
 * @author Michael Albert
 */
public class Universe {
    
    HashMap<Integer, Node> universe = new HashMap<>();
    
    public Universe() {
        
    }
    
    public Universe(Collection<Node> stars) {
        for(Node star : stars) addNode(star);
    }
    
    public Universe(Node[] stars) {
        for(Node star : stars) addNode(star);
    }
    
    void addNode(Node s) {
        if (universe.containsKey(s.id)) return;
        universe.put(s.id, s);
    }
    
    void addProduction(String productionString) {
        Scanner in = new Scanner(productionString);
        Node source = universe.get(in.nextInt());
        Collection<Node> production = new ArrayList<>();
        while (in.hasNextInt()) {
            production.add(universe.get(in.nextInt()));
        }
        source.addProduction(production);        
    }
    
    // A node is remote if it has no children or 
    // (recursively) all of its children are on the edge.
    
    Collection<Node> remoteNodes() {
        
        HashSet<Node> result = new HashSet<>();
        ArrayDeque<Node> q = new ArrayDeque<>();
        for(Node s : universe.values()) {
            if (s.hasNoProductions()) {
                q.offer(s);
            }
        }
        while (!q.isEmpty()) {
            Node s = q.poll();
            if (result.contains(s)) continue;
            result.add(s);
            for (Node t : s.parents()) {
                t.informRemote(s);
                if (t.hasNoProductions()) q.offer(t);
            }
        }
        
        return result; 
    }
    
    HashMap<Integer, Collection<Node>> proof() {
        HashMap<Integer, Collection<Node>> result = new HashMap<>();
        Collection<Node> remotes = remoteNodes();
        for(Node n : universe.values()) {
            if (remotes.contains(n) || result.containsKey(n.id)) continue;
            Deque<Node> q = new ArrayDeque<>();
            q.offer(n);
            while (!q.isEmpty()) {
                Node current = q.poll();
                if (current.hasNoProductions()) {
                    System.out.println("How did you get here?");
                    System.exit(1);
                }
                Collection<Node> cp = current.getProduction();
                result.put(current.id, cp);
                for(Node ncp : cp) {
                    if (!result.containsKey(ncp.id)) q.offer(ncp);
                }
            }
        }
        
        return result;
    }

}
